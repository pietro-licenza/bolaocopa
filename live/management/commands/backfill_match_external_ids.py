"""
backfill_match_external_ids
---------------------------

Populates ``Match.external_id`` (the football-data.org ``match.id``) for
every ``Match`` in the database that does not yet have one, by going
through the ``LiveDataRouter``.

Source priority
================

Per Epic 7 of ``TASKS.md`` and the hybrid strategy documented in
``live/services/router.py``, this command delegates to:

    1. ``FootballDataOrgClient.get_competition_matches`` for the entire
       World Cup 2026 window (one HTTP request — FDO supports date
       ranges, so 104 matches fit in a single call).
    2. ``ApiFootballClient.get_fixtures_by_date`` as a per-day fallback
       when FDO returns nothing (or errors out). The router triggers
       the fallback automatically; this command does not need to know
       which source eventually answered.

Matching strategy
================

For each pending local ``Match`` we look it up in the upstream payload
by:

    (match.match_datetime.date(), normalized(home), normalized(away))

where ``normalized`` is ``unicodedata``-stripped, lower-cased, and
non-alphanumerics removed. The order of ``home``/``away`` is also tried
inverted (some upstreams occasionally swap sides). When a match is
found, the upstream ``id`` is stored on ``Match.external_id``.

For each side we try up to three normalized candidates, in this order:

    1. ``team.name`` (the pt-BR name shown in the UI)
    2. ``team.name_en`` (the English name as used by football-data.org,
       e.g. "United States" / "South Korea" / "Morocco")
    3. ``team.country_code`` (the 3-letter FIFA code, e.g. "USA" /
       "KOR" / "MAR")

TBD placeholder teams (``TBD-H``/``TBD-A``) intentionally yield no
candidates and therefore never match, which is the correct behaviour
for the knockout-stage placeholder matches. The order in which we try
the candidates also tries ``home``/``away`` and ``away``/``home``, so
spelling variants in either side and side-swap upstream bugs both work.

The command is **idempotent**: it only ever touches rows where
``external_id IS NULL`` and only ever writes the ``external_id`` field
via ``QuerySet.update(...)``, so running it multiple times will never
overwrite a previously resolved value.

Flags
=====

* ``--dry-run`` — simulate, do not write to the database.
* ``--no-input`` — do not prompt for confirmation; used by CI/agents.
* ``--date-from`` / ``--date-to`` — override the default 2026 World Cup
  window (defaults are 2026-06-11 .. 2026-07-19).

Rate limiting
=============

FDO free tier is 10 requests/minute; one call covers the whole
tournament. API-Football free tier is 100 requests/day; the fallback
issues at most ~40 calls (one per day in the window). Both numbers
comfortably fit the free quotas.
"""

import re
import unicodedata
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from live.services.router import LiveDataRouter
from matches.models import Match


# Default window for the 2026 FIFA World Cup.
DEFAULT_DATE_FROM = '2026-06-11'
DEFAULT_DATE_TO = '2026-07-19'


def _normalize(text):
    """Lower-case, strip accents, collapse non-alphanumerics."""
    if not text:
        return ''
    decomposed = unicodedata.normalize('NFD', str(text))
    stripped = ''.join(
        char for char in decomposed
        if unicodedata.category(char) != 'Mn'
    )
    stripped = stripped.lower()
    stripped = re.sub(r'[^a-z0-9]+', '', stripped)
    return stripped


class Command(BaseCommand):
    help = (
        'Preenche Match.external_id via LiveDataRouter (FDO primeiro, '
        'API-Football como fallback). Idempotente: so atualiza Matches '
        'com external_id IS NULL.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Nao grava no banco; apenas simula e loga o que seria feito.',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Nao pede confirmacao interativa.',
        )
        parser.add_argument(
            '--date-from',
            default=DEFAULT_DATE_FROM,
            help=(
                'Data inicial (YYYY-MM-DD) da janela de busca. '
                'Padrao: {0}.'.format(DEFAULT_DATE_FROM)
            ),
        )
        parser.add_argument(
            '--date-to',
            default=DEFAULT_DATE_TO,
            help=(
                'Data final (YYYY-MM-DD) da janela de busca. '
                'Padrao: {0}.'.format(DEFAULT_DATE_TO)
            ),
        )

    # ------------------------------------------------------------------
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        no_input = options['no_input']
        date_from = options['date_from']
        date_to = options['date_to']

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '[DRY-RUN] Nenhuma alteracao sera persistida no banco.',
            ))

        # Snapshot of "before" count.
        pending_before = Match.objects.filter(external_id__isnull=True).count()
        self.stdout.write(
            f'Matches sem external_id antes do backfill: {pending_before}'
        )

        if pending_before == 0:
            self.stdout.write(self.style.SUCCESS(
                'Nada a fazer: todos os Matches ja possuem external_id.',
            ))
            return

        if not no_input and not dry_run:
            confirm = input(
                'Isso ira consultar APIs externas e atualizar '
                '{0} Match(es). Continuar? [y/N] '.format(pending_before),
            )
            if confirm.strip().lower() not in ('y', 'yes'):
                self.stdout.write(self.style.WARNING('Abortado pelo usuario.'))
                return

        router = LiveDataRouter()
        upstream = router.find_world_cup_match(date_from, date_to)
        source = self._detect_source(router)
        self.stdout.write(
            f'Resultado do router ({source}): {len(upstream)} partida(s) '
            f'na janela {date_from}..{date_to}.'
        )

        if not upstream:
            self.stdout.write(self.style.ERROR(
                'Nenhuma partida retornada pelas APIs. Nada a fazer.'
            ))
            return

        fixture_index, by_date_count = self._index_upstream(upstream, source)

        # Group pending local matches by date so we only look at fixtures
        # for the same day.
        pending_qs = Match.objects.filter(external_id__isnull=True)
        matches_by_date = defaultdict(list)
        for match in pending_qs.order_by('match_datetime'):
            matches_by_date[match.match_datetime.date()].append(match)

        self.stdout.write(
            f'Datas locais distintas a casar: {len(matches_by_date)}'
        )

        total_updated = 0
        total_unmatched = 0
        dates_without_fixtures = 0

        for match_date in sorted(matches_by_date):
            pending_for_date = list(matches_by_date[match_date])
            date_str = match_date.strftime('%Y-%m-%d')
            fixtures = fixture_index.get(match_date, [])
            if not fixtures:
                dates_without_fixtures += 1
                self.stdout.write(
                    f'  {date_str}: 0 fixtures no router '
                    f'({len(pending_for_date)} match(es) pendente(s)).'
                )
                total_unmatched += len(pending_for_date)
                continue

            self.stdout.write(
                f'  {date_str}: {len(fixtures)} fixture(s) no router '
                f'para {len(pending_for_date)} match(es) pendente(s).'
            )

            for match in pending_for_date:
                fixture, inverted, matched_via = self._find_fixture(
                    match, fixtures,
                )
                if fixture is None:
                    total_unmatched += 1
                    self.stdout.write(
                        f'    [SKIP] {match}: nenhuma fixture encontrada '
                        f'para {match.home_team.name} x {match.away_team.name}.'
                    )
                    continue

                external_id = self._extract_external_id(fixture, source)
                if external_id is None:
                    total_unmatched += 1
                    self.stdout.write(
                        f'    [SKIP] {match}: fixture sem id valido.'
                    )
                    continue

                self.stdout.write(
                    f'    [MATCH] {match} -> external_id {external_id} '
                    f'({source}, {"invertido" if inverted else "direto"}, '
                    f'casado por {matched_via})'
                )

                if dry_run:
                    total_updated += 1
                    continue

                with transaction.atomic():
                    # update() keeps the save minimal and prevents any
                    # signal or auto_now on other fields from firing.
                    Match.objects.filter(pk=match.pk).update(
                        external_id=external_id,
                    )
                total_updated += 1

        # Final report.
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=== Resumo ==='))
        self.stdout.write(f'  Fonte utilizada: {source}')
        self.stdout.write(f'  Partidas retornadas pelo router: {len(upstream)}')
        self.stdout.write(f'  Datas locais sem fixtures: {dates_without_fixtures}')
        self.stdout.write(f'  Matches atualizados: {total_updated}')
        self.stdout.write(f'  Matches nao encontrados: {total_unmatched}')

        if not dry_run:
            pending_after = Match.objects.filter(
                external_id__isnull=True,
            ).count()
            self.stdout.write(
                f'  Matches sem external_id apos backfill: {pending_after}'
            )
        else:
            self.stdout.write(self.style.WARNING(
                '  [DRY-RUN] contagem "apos" nao foi consultada.',
            ))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _detect_source(self, router):
        """Return a short source tag ('[FDO]' or '[API-Football]') for logging.

        We look at what the router cached during ``find_world_cup_match``
        to decide which upstream actually served the result.
        """
        for key, value in router._cache.items():
            if not (isinstance(key, tuple) and key and key[0] == 'find_world_cup_match'):
                continue
            if value:
                # The router tried FDO first. We can't tell from the cache
                # alone whether FDO or the per-day fallback served the
                # final payload, so we use a heuristic: the per-day
                # fallback would have called ``get_fixtures_by_date`` on
                # the API-Football client. If FDO had data, the router
                # short-circuits and never touches API-Football, so the
                # FDO client's underlying urllib call is the only one.
                # In practice we just inspect which client produced the
                # items by shape (FDO has 'utcDate' / 'homeTeam', while
                # API-Football has 'fixture.id' / 'teams.home').
                if value and 'homeTeam' in value[0] and 'utcDate' in value[0]:
                    return '[FDO]'
                if value and 'fixture' in value[0] and 'teams' in value[0]:
                    return '[API-Football]'
        # Fallback when the cache was empty or the shape didn't match.
        return '[router]'

    def _index_upstream(self, upstream, source):
        """Build a (date, (home_norm, away_norm)) -> fixture index.

        For each fixture, multiple normalized key variants are inserted
        so that lookups can succeed by:

        * the canonical English name (e.g. "United States")
        * the 3-letter FIFA code (e.g. "USA")
        * the area.name field (FDO-specific, e.g. "Iran" vs team "Iran")

        The first successful lookup wins. We deliberately use a single
        fixture per (home_norm, away_norm) key, so the first-seen variant
        is the one that gets stored; later variants pointing to the same
        key are silently overwritten with the same value.

        Returns the index plus a counter of fixtures per date.
        """
        index = defaultdict(dict)
        per_date = defaultdict(int)
        for fixture in upstream:
            parsed = self._parse_fixture(fixture, source)
            if parsed is None:
                continue
            match_date, home_norm, away_norm, home_tla, away_tla = parsed
            # Primary key: (name, name) - what the FDO actually returns.
            primary = (home_norm, away_norm)
            index[match_date][primary] = fixture
            # TLA fallback: (tla, tla) - cheap to try too.
            if home_tla and away_tla:
                tla_key = (home_tla, away_tla)
                index[match_date].setdefault(tla_key, fixture)
            per_date[match_date] += 1
        return index, per_date

    def _parse_fixture(self, fixture, source):
        """Return (date, home_norm, away_norm, home_tla, away_tla).

        Handles both payload shapes:

        * football-data.org:
          ``{"utcDate": "2026-06-11T19:00:00Z",
             "homeTeam": {"name": ..., "tla": ...},
             "awayTeam": {"name": ..., "tla": ...}, ...}``
        * API-Football:
          ``{"fixture": {"id": ..., "date": "2026-06-11T19:00:00Z"},
             "teams": {"home": {"name": ...}, "away": {"name": ...}}}``

        The TLA (3-letter FIFA code) is used as a secondary matching key
        because some FDO payloads put a different string in the team's
        ``shortName`` (e.g. "USA" vs "United States") but always expose
        the same TLA. API-Football does not expose a TLA in the fixture
        payload, so the second tuple element comes back empty.
        """
        try:
            if 'homeTeam' in fixture and 'utcDate' in fixture:
                # FDO shape.
                utc = fixture['utcDate']
                date_str = utc.split('T', 1)[0]
                home = fixture['homeTeam']['name']
                away = fixture['awayTeam']['name']
                home_tla = fixture['homeTeam'].get('tla') or ''
                away_tla = fixture['awayTeam'].get('tla') or ''
            elif 'teams' in fixture and 'fixture' in fixture:
                # API-Football shape.
                utc = fixture['fixture']['date']
                date_str = utc.split('T', 1)[0]
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                home_tla = ''
                away_tla = ''
            else:
                return None
        except (KeyError, TypeError, AttributeError):
            return None

        from datetime import date as date_type
        try:
            match_date = date_type.fromisoformat(date_str)
        except ValueError:
            return None

        return (
            match_date,
            _normalize(home),
            _normalize(away),
            _normalize(home_tla),
            _normalize(away_tla),
        )

    def _candidate_keys(self, team):
        """Return a list of normalized candidate keys for a Team.

        Order matters: the first non-empty candidate is the most
        authoritative one (the pt-BR ``name`` shown in the UI). The
        English name is next, then the 3-letter FIFA code as a last
        resort. TBD placeholders intentionally yield no candidate.
        """
        candidates = []
        for raw in (team.name, team.name_en, team.country_code):
            normalized = _normalize(raw)
            if normalized:
                candidates.append(normalized)
        return candidates

    def _find_fixture(self, match, fixtures):
        """Return (fixture, inverted, matched_via) or (None, ...) when no match.

        ``matched_via`` is a short human label used in the per-match log
        line so the operator can see which spelling ended up resolving
        the mapping (e.g. "name_en=Brazil" or "country_code=USA").
        """
        home_candidates = self._candidate_keys(match.home_team)
        away_candidates = self._candidate_keys(match.away_team)
        if not home_candidates or not away_candidates:
            return None, False, ''

        for inverted in (False, True):
            h_cands = away_candidates if inverted else home_candidates
            a_cands = home_candidates if inverted else away_candidates
            for h in h_cands:
                for a in a_cands:
                    fixture = fixtures.get((h, a))
                    if fixture is not None:
                        matched_via = self._label_for_match(
                            match.home_team if not inverted else match.away_team,
                            match.away_team if not inverted else match.home_team,
                            h, a,
                        )
                        return fixture, inverted, matched_via
        return None, False, ''

    def _label_for_match(self, home_team, away_team, home_norm, away_norm):
        """Return a short label like 'name_en=USA, country_code=USA' for logs."""
        labels = []
        for raw, role in (
            (home_team.name, 'name'),
            (home_team.name_en, 'name_en'),
            (home_team.country_code, 'country_code'),
        ):
            if _normalize(raw) == home_norm:
                labels.append(f'{role}={raw}')
                break
        for raw, role in (
            (away_team.name, 'name'),
            (away_team.name_en, 'name_en'),
            (away_team.country_code, 'country_code'),
        ):
            if _normalize(raw) == away_norm:
                labels.append(f'{role}={raw}')
                break
        return ' x '.join(labels)

    def _extract_external_id(self, fixture, source):
        """Return the upstream primary id from a fixture dict."""
        try:
            if 'homeTeam' in fixture and 'id' in fixture:
                # FDO wraps the id at the top level of the match object.
                return int(fixture['id'])
            if 'fixture' in fixture and isinstance(fixture['fixture'], dict):
                return int(fixture['fixture']['id'])
        except (KeyError, TypeError, ValueError):
            return None
        return None
