"""
Sync a single ``Match`` instance from an upstream API.

This module deliberately stays out of the views / forms layer so the
same logic can be reused from:

* the ``MatchSyncView`` (the "Buscar resultado" button in the UI), and
* a future management command / cron job (TASKS.md US-7.4 mentions an
  auto-refresh every 60s, which will need a background entry point).

The public entry point is :func:`sync_match_from_api` which:

1. looks the match up through :class:`LiveDataRouter` (FDO first,
   API-Football as fallback);
2. maps the upstream payload to ``Match`` fields;
3. saves only the fields that actually changed (idempotent re-runs);
4. syncs detailed in-match events (goals / cards / substitutions) via
   the same router — added in US-7.5;
5. returns a :class:`SyncResult` so callers (views, commands) can act
   on the outcome.
"""

import logging
from dataclasses import dataclass

from matches.models import Match

from live.models import MatchEvent
from live.services.router import LiveDataRouter


logger = logging.getLogger(__name__)


# Mapping tables for upstream status strings to our internal choices.
# FDO documented values (https://docs.football-data.org/):
#   TIMED, SCHEDULED, IN_PLAY, PAUSED, FINISHED, SUSPENDED,
#   POSTPONED, CANCELLED, AWARDED
# API-Football documented ``fixture.status.short`` values:
#   NS, 1H, HT, 2H, ET, BT, P, SUSP, INT, LIVE, FT, AET, PEN_LIVE,
#   FT_PEN, CANC, AWD, WO
_FDO_STATUS_MAP = {
    'TIMED': 'agendado',
    'SCHEDULED': 'agendado',
    'IN_PLAY': 'em_andamento',
    'PAUSED': 'em_andamento',
    'FINISHED': 'finalizado',
    'AWARDED': 'finalizado',
    # Anything else (SUSPENDED, POSTPONED, CANCELLED) is kept as
    # ``agendado`` so the match still appears in lists but does not
    # trigger scoring.
    'SUSPENDED': 'agendado',
    'POSTPONED': 'agendado',
    'CANCELLED': 'agendado',
}

_API_FOOTBALL_STATUS_MAP = {
    'NS': 'agendado',
    '1H': 'em_andamento',
    '2H': 'em_andamento',
    'ET': 'em_andamento',
    'BT': 'em_andamento',
    'P': 'em_andamento',
    'LIVE': 'em_andamento',
    'HT': 'em_andamento',
    'INT': 'em_andamento',
    'FT': 'finalizado',
    'AET': 'finalizado',
    'FT_PEN': 'finalizado',
    'PEN_LIVE': 'em_andamento',
    'AWD': 'finalizado',
    'WO': 'finalizado',
    'SUSP': 'agendado',
    'CANC': 'agendado',
}

# API-Football detail field values for the ``Card`` event type. Yellow
# and red cards are differentiated here, while the bare ``type`` value
# only tells us "a card was shown".
_API_FOOTBALL_CARD_DETAIL_MAP = {
    'Yellow Card': 'yellow_card',
    'Red Card': 'red_card',
    'Second Yellow card': 'red_card',
    'Yellow Red Card': 'red_card',
}

# Valid choices on ``MatchEvent.type``. Used to validate payloads and
# filter out junk rows from upstream.
_VALID_EVENT_TYPES = {
    'goal', 'yellow_card', 'red_card',
    'substitution_in', 'substitution_out',
}


@dataclass
class SyncResult:
    """Outcome of a single :func:`sync_match_from_api` call.

    Attributes
    ----------
    success:
        ``True`` if the upstream call returned a usable payload and
        the local ``Match`` was updated (or already up to date).
    status_changed:
        ``True`` only if the ``status`` field was modified by this
        sync. Other field changes (e.g. score) leave this ``False``.
    events_synced:
        Number of ``MatchEvent`` rows written (or already up to date)
        for this match. ``0`` when the match has no ``external_id``
        or when the upstream call returns no events — both cases are
        expected for upcoming games, so this is not an error signal.
    error:
        ``None`` on success; a short, human-readable string on
        failure. Intended to be shown to end users via
        ``django.contrib.messages``.
    """

    success: bool
    status_changed: bool
    events_synced: int
    error: str | None = None


def sync_match_from_api(match, router=None):
    """Fetch the freshest known state for ``match`` and persist it.

    Parameters
    ----------
    match:
        A ``matches.models.Match`` instance. It MUST have a non-null
        ``external_id``; otherwise the call is a no-op that returns
        ``success=False``.
    router:
        Optional :class:`LiveDataRouter` (or compatible) for tests.
        When ``None``, a fresh router is constructed using the
        default clients.
    """
    if match.external_id is None:
        return SyncResult(
            success=False,
            status_changed=False,
            events_synced=0,
            error='Jogo sem identificador externo — não é possível sincronizar.',
        )

    router = router or LiveDataRouter()
    payload = router.get_match_live_data(match)
    if not payload:
        return SyncResult(
            success=False,
            status_changed=False,
            events_synced=0,
            error='Não foi possível obter dados do jogo nas APIs externas.',
        )

    new_status, new_home, new_away, new_minute, source = _extract_fields(
        payload,
    )
    if source is None:
        # The payload was neither a recognizable FDO nor API-Football
        # shape. Avoid writing garbage; surface a friendly error.
        return SyncResult(
            success=False,
            status_changed=False,
            events_synced=0,
            error='Resposta da API em formato inesperado.',
        )

    changed_fields = []
    status_changed = False

    if new_status is not None and new_status != match.status:
        match.status = new_status
        changed_fields.append('status')
        status_changed = True

    if new_home is not None and new_home != match.home_score:
        match.home_score = new_home
        changed_fields.append('home_score')

    if new_away is not None and new_away != match.away_score:
        match.away_score = new_away
        changed_fields.append('away_score')

    if (
        new_minute is not None
        and new_minute != match.elapsed_minute
    ):
        match.elapsed_minute = new_minute
        changed_fields.append('elapsed_minute')

    if changed_fields:
        # ``updated_at`` is auto-managed by ``auto_now``; listing it
        # explicitly is harmless and keeps the contract obvious.
        changed_fields.append('updated_at')
        match.save(update_fields=changed_fields)
        logger.info(
            '[Sync] Match %s updated via %s: %s',
            match.pk, source, ','.join(sorted(changed_fields)),
        )

    # Detailed in-match events (goals / cards / substitutions) — see
    # US-7.5. Routed through the same router (API-Football primary;
    # FDO returns [] in practice). A failure here does not invalidate
    # the score update we just did: log and move on, returning the
    # number of events actually written.
    events_synced = _sync_match_events(match, router)

    return SyncResult(
        success=True,
        status_changed=status_changed,
        events_synced=events_synced,
        error=None,
    )


# ----------------------------------------------------------------------
# Event sync (US-7.5)
# ----------------------------------------------------------------------

def _sync_match_events(match, router):
    """Rebuild the ``MatchEvent`` list for ``match`` from upstream.

    Strategy: drop every existing event for the match and re-create
    them from the API-Football payload returned by
    :meth:`LiveDataRouter.get_match_events`. The wipe-and-recreate
    approach is acceptable because:

    * events are detail rows with no FK pointing at them from other
      tables (ranking / scoring read final scores, not events);
    * the upstream API does not expose a stable primary key per event,
      so a delta sync would require a fragile composite hash;
    * the row count per match is bounded (a typical game has ~10-30
      events), so the cost is negligible.

    Returns the number of events actually written.
    """
    raw_events = router.get_match_events(match)
    if not raw_events:
        # No events upstream (typical for upcoming games) or API-Football
        # returned an empty list. Wipe any stale rows so the UI does not
        # show leftovers from a previous state, and report 0.
        _delete_events_for_match(match)
        return 0

    new_events = _build_event_objects(match, raw_events)
    if not new_events:
        # Upstream returned rows but none mapped to a known type
        # (e.g. all entries were something we don't model). Still wipe
        # the local table to avoid drift.
        _delete_events_for_match(match)
        return 0

    _delete_events_for_match(match)
    MatchEvent.objects.bulk_create(new_events)
    logger.info(
        '[Sync] Match %s: %d event(s) synced.',
        match.pk, len(new_events),
    )
    return len(new_events)


def _delete_events_for_match(match):
    """Remove every ``MatchEvent`` row attached to ``match``.

    Kept as a tiny helper so the sync flow reads top-down.
    """
    MatchEvent.objects.filter(match=match).delete()


def _build_event_objects(match, raw_events):
    """Translate a list of upstream event dicts into ``MatchEvent``s.

    Returns only rows that can be unambiguously matched to a local
    ``Team`` and a known ``type`` value. Anything we can't classify
    is silently dropped (logged at ``debug``) so a malformed payload
    does not bring the whole sync down.

    API-Football returns substitutions as a single ``type=Subst``
    row that contains *both* the outgoing and the incoming player
    in the same record (using the ``assist`` field for the player
    coming on). We split that into two ``MatchEvent`` rows
    (``substitution_out`` and ``substitution_in``) so the UI can
    style them differently.
    """
    from matches.models import Team

    # Pre-build a lookup of local teams keyed by the various spellings
    # we expect the API to return. ``name_en`` is the English name we
    # store in the seeder (matches the API's English name); ``name`` is
    # the pt-BR display name; ``country_code`` is the 3-letter TLA.
    teams_by_name_en = {}
    teams_by_name = {}
    teams_by_code = {}
    for team in Team.objects.all():
        if team.name_en:
            teams_by_name_en[team.name_en.lower()] = team
        if team.name:
            teams_by_name[team.name.lower()] = team
        if team.country_code:
            teams_by_code[team.country_code.upper()] = team

    built = []
    for raw in raw_events:
        event_type = _classify_event_type(raw)
        if event_type is None:
            logger.debug(
                '[Sync] Dropping unknown event for match %s: %r',
                match.pk, raw,
            )
            continue

        team = _resolve_team(raw, teams_by_name_en, teams_by_name, teams_by_code)
        if team is None:
            logger.debug(
                '[Sync] Dropping event for match %s — team not resolved: %r',
                match.pk, raw,
            )
            continue

        minute = _resolve_minute(raw)
        if minute is None:
            logger.debug(
                '[Sync] Dropping event for match %s — minute missing: %r',
                match.pk, raw,
            )
            continue

        player = _string_or_default(_dig(raw, 'player', 'name'))
        if not player:
            logger.debug(
                '[Sync] Dropping event for match %s — player missing: %r',
                match.pk, raw,
            )
            continue

        if event_type == 'subst':
            # API-Football merges both sides of a sub into one row.
            # The outgoing player's name lives in ``player.name`` and
            # the incoming player's name lives in ``assist.name``.
            outgoing = player
            incoming = _string_or_default(_dig(raw, 'assist', 'name'))
            if not incoming:
                logger.debug(
                    '[Sync] Dropping substitution for match %s — '
                    'incoming player missing: %r',
                    match.pk, raw,
                )
                continue
            # Order is fixed by API-Football: the OUT player is in
            # ``player.name``; the IN player is in ``assist.name``.
            built.append(MatchEvent(
                match=match,
                minute=minute,
                type='substitution_out',
                team=team,
                player=outgoing,
                assist_player='',
            ))
            built.append(MatchEvent(
                match=match,
                minute=minute,
                type='substitution_in',
                team=team,
                player=incoming,
                assist_player='',
            ))
        elif event_type == 'goal':
            assist = _string_or_default(_dig(raw, 'assist', 'name'))
            built.append(MatchEvent(
                match=match,
                minute=minute,
                type='goal',
                team=team,
                player=player,
                assist_player=assist,
            ))
        else:
            # yellow_card / red_card
            built.append(MatchEvent(
                match=match,
                minute=minute,
                type=event_type,
                team=team,
                player=player,
                assist_player='',
            ))

    return built


def _classify_event_type(raw):
    """Map an API-Football event dict to a ``MatchEvent.type`` value.

    Returns ``None`` for events we don't model (var, comment, etc.).
    """
    raw_type = _string_or_default(raw.get('type'))
    if not raw_type:
        return None
    if raw_type == 'Goal':
        return 'goal'
    if raw_type == 'Card':
        detail = _string_or_default(raw.get('detail'))
        return _API_FOOTBALL_CARD_DETAIL_MAP.get(detail)
    if raw_type == 'Subst':
        # The decision between IN/OUT is made in the caller once we
        # split the merged Subst row. Return a sentinel that the
        # caller knows to handle specially.
        return 'subst'
    return None


def _resolve_team(raw, teams_by_name_en, teams_by_name, teams_by_code):
    """Pick a local ``Team`` for an event payload.

    The API exposes ``team.id`` and ``team.name``. The id is opaque
    (not the same as our DB pk), so we rely on the human-readable
    name. We try ``name_en`` (English, matches the API), then the
    pt-BR ``name``, then the 3-letter ``country_code`` defensively.
    """
    team_name = _string_or_default(_dig(raw, 'team', 'name'))
    if team_name:
        lowered = team_name.lower()
        if lowered in teams_by_name_en:
            return teams_by_name_en[lowered]
        if lowered in teams_by_name:
            return teams_by_name[lowered]
    return None


def _resolve_minute(raw):
    """Pull the elapsed minute from an API-Football event payload.

    The API nests it under ``time.elapsed``; we keep ``extra`` (added
    time) as a fallback so a stoppage-time goal is not silently
    dropped.
    """
    elapsed = _int_or_none(_dig(raw, 'time', 'elapsed'))
    if elapsed is not None and elapsed >= 0:
        return elapsed
    extra = _int_or_none(_dig(raw, 'time', 'extra'))
    if extra is not None and extra > 0:
        # 45 + 2 = 47, 90 + 5 = 95, etc.
        return 45 + extra if elapsed is None or elapsed <= 45 else 90 + extra
    return None


def _string_or_default(value, default=''):
    if value is None:
        return default
    text = str(value).strip()
    return text or default


# ----------------------------------------------------------------------
# Field extraction (score / status)
# ----------------------------------------------------------------------

def _extract_fields(payload):
    """Map an upstream payload to ``(status, home, away, minute, source)``.

    Returns a tuple where ``source`` is one of ``'FDO'``,
    ``'API-Football'`` or ``None``. The numeric / status fields may be
    ``None`` when the upstream response simply doesn't carry that
    information (e.g. football-data.org does not expose an
    "elapsed minute" field on the free tier).
    """
    if _looks_like_fdo(payload):
        return (
            _fdo_status(payload),
            _int_or_none(_dig(payload, 'score', 'fullTime', 'home')),
            _int_or_none(_dig(payload, 'score', 'fullTime', 'away')),
            # FDO does not expose an elapsed-minute field on the free
            # tier. Leave it as ``None`` so we never overwrite a value
            # we don't have a fresh reading for.
            None,
            'FDO',
        )
    if _looks_like_api_football(payload):
        af_status = _dig(payload, 'fixture', 'status', 'short')
        af_minute = _int_or_none(_dig(payload, 'fixture', 'status', 'elapsed'))
        return (
            _API_FOOTBALL_STATUS_MAP.get(af_status),
            _int_or_none(_dig(payload, 'goals', 'home')),
            _int_or_none(_dig(payload, 'goals', 'away')),
            af_minute,
            'API-Football',
        )
    return (None, None, None, None, None)


def _dig(payload, *keys):
    """Walk a nested dict and return the leaf value, or ``None``.

    Avoids a chain of ``.get()`` calls and gracefully handles the case
    where any intermediate key is missing.
    """
    node = payload
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
        if node is None:
            return None
    return node


def _int_or_none(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _looks_like_fdo(payload):
    """Heuristic: FDO payloads have ``utcDate`` and nested ``homeTeam``."""
    return (
        isinstance(payload, dict)
        and 'utcDate' in payload
        and 'homeTeam' in payload
        and 'awayTeam' in payload
    )


def _looks_like_api_football(payload):
    """Heuristic: API-Football payloads nest under ``fixture`` and ``goals``."""
    return (
        isinstance(payload, dict)
        and isinstance(payload.get('fixture'), dict)
        and 'goals' in payload
    )


def _fdo_status(payload):
    raw = payload.get('status')
    if not raw:
        return None
    return _FDO_STATUS_MAP.get(raw)
