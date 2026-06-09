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
4. returns a :class:`SyncResult` so callers (views, commands) can act
   on the outcome.

Per US-7.3 scope, **no events are synced here** — that lives in US-7.5
and will reuse the same router but plug into a separate ``MatchEvent``
table.
"""

import logging
from dataclasses import dataclass

from matches.models import Match

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
        Always ``0`` in US-7.3. The field is kept on the dataclass so
        US-7.5 can populate it without breaking callers.
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

    return SyncResult(
        success=True,
        status_changed=status_changed,
        events_synced=0,
        error=None,
    )


# ----------------------------------------------------------------------
# Field extraction
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
