"""
HTTP views for the ``matches`` app.

This module groups two kinds of views:

* **Legacy list view** (:class:`MatchListView`) — the original
  "all matches" page built for US-4.1. Kept under ``/matches/all/``
  so the new "Jogos" landing page can own the ``/matches/`` root.

* **US-7.7 dedicated sub-views** — :class:`MatchHomeView`,
  :class:`MatchScheduleView`, :class:`MatchGroupsView` and
  :class:`MatchBracketView`. Together they form the new "Jogos" tab
  on the navbar with three sub-areas (Agenda, Grupos, Chaveamento).

All authenticated views in this module use :class:`LoginRequiredMixin`
as the first mixin so the project rule ("CBVs only, LoginRequiredMixin
first") holds without exceptions. The point calculation logic itself
lives in ``matches.signals`` (not here) and is triggered by Django
signals when a match is finalised.
"""

import datetime
import logging
from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView, TemplateView

from predictions.models import Prediction

from .groups_data import (
    WORLD_CUP_2026_GROUPS,
    get_all_groups,
    get_group_for_team,
)
from .models import Match, Round, Team


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Legacy list view (US-4.1)
# ---------------------------------------------------------------------------


class MatchListView(LoginRequiredMixin, ListView):
    """Flat list of every match, paginated, newest first.

    This is the original "Jogos" page from US-4.1. It was displaced
    by the new :class:`MatchHomeView` landing page introduced in
    US-7.7, so it now lives at ``/matches/all/`` (see
    ``matches.urls``). The ``match_list`` URL name is preserved for
    backwards compatibility with templates / views that still
    ``{% url "match_list" %}`` or ``reverse('match_list')`` on it.
    """

    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.select_related(
            'home_team', 'away_team', 'stadium', 'round',
        ).order_by('match_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pool_match_ids = set(
            Prediction.objects.filter(
                user=self.request.user,
            ).values_list('match_id', flat=True)
        )
        match_items = []
        for match in context['matches']:
            match_items.append({
                'match': match,
                'home_team': match.home_team,
                'away_team': match.away_team,
                'match_datetime': match.match_datetime,
                'stadium': match.stadium,
                'round': match.round,
                'status': match.status,
                'user_has_predicted': match.pk in user_pool_match_ids,
            })
        context['match_items'] = match_items
        context['upcoming_count'] = Match.objects.filter(
            status='agendado',
        ).count()
        context['finished_count'] = Match.objects.filter(
            status='finalizado',
        ).count()
        return context


# ---------------------------------------------------------------------------
# US-7.7: dedicated "Jogos" sub-views
# ---------------------------------------------------------------------------


# ``today()`` is a small helper instead of a top-level constant so the
# view re-evaluates it on every request — important because Django
# boots once per process and a process can serve many days.
def _today():
    return timezone.localdate()


class MatchHomeView(LoginRequiredMixin, TemplateView):
    """Landing page for the "Jogos" navbar entry.

    Renders three big navigation cards pointing at the sub-views:

    * **Agenda** — :class:`MatchScheduleView` (today's matches, with
      a date picker to navigate to any other day).
    * **Grupos** — :class:`MatchGroupsView` (the A-L group table with
      computed standings).
    * **Chaveamento** — :class:`MatchBracketView` (the knockout
      bracket; TBDs until the group stage resolves).

    The card metadata (label, href, SVG path, accent color) is
    pre-computed in :meth:`get_context_data` so the template stays a
    thin renderer. We do not raise on the missing template here:
    Django's CBV machinery returns a 500 with a clear traceback that
    is far more useful than a silent 404.
    """

    template_name = 'matches/match_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today_iso = _today().isoformat()
        context['sub_links'] = [
            {
                'label': 'Agenda',
                'description': 'Veja os jogos do dia e navegue por data.',
                'href_label': '/matches/schedule/',
                'url': f'/matches/schedule/{today_iso}/',
                'icon_path': 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
                'accent': 'emerald',
            },
            {
                'label': 'Grupos',
                'description': 'Tabela completa dos 12 grupos com classificação atualizada.',
                'href_label': '/matches/groups/',
                'url': '/matches/groups/',
                'icon_path': 'M4 6h6v6H4V6zm10 0h6v6h-6V6zM4 16h6v4H4v-4zm10 0h6v4h-6v-4z',
                'accent': 'sky',
            },
            {
                'label': 'Chaveamento',
                'description': 'Acompanhe o mata-mata: 16-avos ate a final.',
                'href_label': '/matches/bracket/',
                'url': '/matches/bracket/',
                'icon_path': 'M3 4h18v4H3V4zm0 6h6v10H3V10zm10 0h8v10h-8V10z',
                'accent': 'amber',
            },
        ]
        return context


class MatchScheduleView(LoginRequiredMixin, ListView):
    """List the matches of a single day, paginated.

    The day comes from (in order of precedence):

    1. The ``<date:date>`` URL kwarg, when ``/matches/schedule/YYYY-MM-DD/``
       is requested.
    2. The ``?date=YYYY-MM-DD`` query string parameter.
    3. Today (in the project timezone — America/Sao_Paulo).

    The view does not raise on an invalid date — that work is done
    by the URL converter (it produces a 404). Empty / no-match days
    are rendered gracefully via the standard ``empty`` template path.

    The list also exposes ``available_dates`` (a 30-day window of
    distinct match dates) so the template can render a date picker
    or quick-jump buttons without re-querying the database.
    """

    model = Match
    template_name = 'matches/match_schedule.html'
    context_object_name = 'matches'
    paginate_by = 50

    def get_date(self):
        """Return the :class:`datetime.date` to render.

        Priority: URL kwarg > query string > today.
        """
        url_date = self.kwargs.get('date')
        if isinstance(url_date, datetime.date):
            return url_date
        query_date = self.request.GET.get('date')
        if query_date:
            try:
                return datetime.date.fromisoformat(query_date)
            except ValueError:
                # Fall through to today; the template can flag a
                # soft warning via the ``invalid_date`` flag.
                self._invalid_date = True
        return _today()

    def get_queryset(self):
        selected = self.get_date()
        return (
            Match.objects
            .filter(match_datetime__date=selected)
            .select_related('home_team', 'away_team', 'stadium', 'round')
            .order_by('match_datetime')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected = self.get_date()
        context['selected_date'] = selected
        context['selected_date_iso'] = selected.isoformat()
        context['invalid_date'] = getattr(self, '_invalid_date', False)
        # Distinct dates (within a 30-day forward window + 7 days
        # backwards) that have at least one match scheduled. Sorted
        # chronologically so the template can render a stable
        # date picker.
        today = _today()
        window_start = today - datetime.timedelta(days=7)
        window_end = today + datetime.timedelta(days=30)
        context['available_dates'] = list(
            Match.objects
            .filter(match_datetime__date__gte=window_start)
            .filter(match_datetime__date__lte=window_end)
            .dates('match_datetime', 'day')
        )
        return context


class MatchGroupsView(LoginRequiredMixin, TemplateView):
    """Render the A-L group table with computed standings.

    The :class:`Team` model has no ``group`` field (groups change
    every World Cup), so the grouping is read from
    :data:`matches.groups_data.WORLD_CUP_2026_GROUPS` — the official
    draw of December 5, 2025. For each group we compute the
    standings locally from finished matches; if the football-data.org
    API is reachable we merge its ``/standings`` payload as a
    snapshot (used as authoritative where the local computation is
    empty), but the local computation always runs as a fallback.

    Ranking criteria — same as the official FIFA tie-breakers used
    during the tournament, simplified to the most common subset:

    1. Points (3 / 1 / 0)
    2. Goal difference
    3. Goals scored
    4. Alphabetical team name (stable sort key for ties on every
       other criterion)
    """

    template_name = 'matches/match_groups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Read-only access to FDO is best-effort; the local
        # calculation is the canonical source of truth. Errors are
        # logged and swallowed.
        fdo_snapshot = self._get_fdo_snapshot()
        standings = self._compute_local_standings(fdo_snapshot)
        # Build the per-group "roster" (list of teams in draw order)
        # so the template can show the four flags / names even when
        # no matches have been played yet.
        groups_roster = {}
        for letter, codes in WORLD_CUP_2026_GROUPS.items():
            groups_roster[letter] = list(
                self._teams_by_codes(codes)
            )
        # Build a parallel {group_letter: {team_pk: row_dict}} index so
        # the template can look up a team's stats by primary key while
        # iterating the full 4-team roster (needed to always render
        # all 4 teams, not just the ones that have already played).
        standings_by_team = {}
        for letter, rows in standings.items():
            standings_by_team[letter] = {
                row['team'].pk: row for row in rows
            }
        context['groups'] = groups_roster
        context['standings'] = standings
        context['standings_by_team'] = standings_by_team
        context['group_letters'] = get_all_groups()
        return context

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _teams_by_codes(self, codes):
        """Return :class:`Team` objects in the same order as ``codes``.

        TBD placeholders are not real teams for the group stage and
        are dropped here — the bracket view deals with them.
        """
        teams_by_code = {
            t.country_code: t
            for t in Team.objects.filter(country_code__in=codes)
        }
        return [teams_by_code[code] for code in codes if code in teams_by_code]

    def _compute_local_standings(self, fdo_snapshot):
        """Build the standings dict from finished matches.

        Returns ``{group_letter: [{team, P, J, V, E, D, GP, GC, SG,
        position}, ...], ...}`` with positions already assigned in
        rank order. When FDO has data for a team and the local
        computation has none (e.g. group stage not yet started),
        the FDO row is merged in as-is.
        """
        from .models import Team

        # Aggregate all finished group-stage matches. We do this in
        # Python rather than SQL because the per-team rollup is
        # tiny (4 teams * 6 matches per group) and the logic is
        # easier to read this way.
        finished = (
            Match.objects
            .filter(status='finalizado', round__phase='grupo')
            .filter(home_score__isnull=False, away_score__isnull=False)
            .select_related('home_team', 'away_team')
        )
        # {group_letter: {team_id: stats_dict}}
        stats = defaultdict(dict)

        def _ensure(team):
            letter = get_group_for_team(team.country_code)
            if not letter:
                return None
            bucket = stats[letter]
            if team.pk not in bucket:
                bucket[team.pk] = {
                    'team': team,
                    'P': 0, 'J': 0, 'V': 0, 'E': 0, 'D': 0,
                    'GP': 0, 'GC': 0, 'SG': 0,
                }
            return bucket[team.pk]

        for match in finished:
            home = _ensure(match.home_team)
            away = _ensure(match.away_team)
            if home is None or away is None:
                # Match involves a non-group team (should not happen
                # for phase='grupo' but guard anyway).
                continue
            home['J'] += 1
            away['J'] += 1
            home['GP'] += match.home_score
            home['GC'] += match.away_score
            away['GP'] += match.away_score
            away['GC'] += match.home_score
            if match.home_score > match.away_score:
                home['V'] += 1
                home['P'] += 3
                away['D'] += 1
            elif match.home_score < match.away_score:
                away['V'] += 1
                away['P'] += 3
                home['D'] += 1
            else:
                home['E'] += 1
                away['E'] += 1
                home['P'] += 1
                away['P'] += 1

        # Build the output, sorted per group, with FDO merging.
        out = {}
        # Pre-fetch the full draw roster once so we can fill in any
        # team that has neither local nor FDO data (e.g. group stage
        # not yet started, or FDO unreachable). This ensures every
        # group always has 4 rows, one per team, with a proper
        # 1-4 position assigned after sorting.
        roster_by_letter = {
            letter: list(self._teams_by_codes(codes))
            for letter, codes in WORLD_CUP_2026_GROUPS.items()
        }
        for letter in get_all_groups():
            group_stats = list(stats.get(letter, {}).values())
            # If the FDO has data for some team in this group and we
            # have no local row for it (e.g. group stage hasn't
            # started), seed the team with zeros so it still shows
            # up in the table.
            fdo_rows_by_team = (
                fdo_snapshot.get(letter, {}) if fdo_snapshot else {}
            )
            seen_pks = {row['team'].pk for row in group_stats}
            for fdo_team, fdo_row in fdo_rows_by_team.items():
                if fdo_team.pk in seen_pks:
                    continue
                group_stats.append({
                    'team': fdo_team,
                    'P': fdo_row.get('points', 0),
                    'J': fdo_row.get('played', 0),
                    'V': fdo_row.get('won', 0),
                    'E': fdo_row.get('draw', 0),
                    'D': fdo_row.get('lost', 0),
                    'GP': fdo_row.get('goals_for', 0),
                    'GC': fdo_row.get('goals_against', 0),
                    'SG': 0,
                })
            # Fallback: any team in the draw that still has no row
            # (no local stats and no FDO data) gets a zeroed row so
            # every group renders 4 teams with positions 1-4.
            seen_pks = {row['team'].pk for row in group_stats}
            for team in roster_by_letter.get(letter, []):
                if team.pk in seen_pks:
                    continue
                group_stats.append({
                    'team': team,
                    'P': 0, 'J': 0, 'V': 0, 'E': 0, 'D': 0,
                    'GP': 0, 'GC': 0, 'SG': 0,
                })
            # Compute SG last so it always reflects the final
            # GP/GC values (local or merged).
            for row in group_stats:
                row['SG'] = row['GP'] - row['GC']
            # Sort: P desc, SG desc, GP desc, name asc.
            group_stats.sort(key=lambda r: (
                -r['P'],
                -r['SG'],
                -r['GP'],
                r['team'].name.lower(),
            ))
            for position, row in enumerate(group_stats, start=1):
                row['position'] = position
            out[letter] = group_stats
        return out

    def _get_fdo_snapshot(self):
        """Best-effort FDO ``/standings`` snapshot.

        Returns ``{group_letter: {team: {points, played, won, draw,
        lost, goals_for, goals_against}}}`` or ``None`` if the API
        is unavailable / returns nothing useful.

        Imports of the live API client are local to avoid loading
        urllib + certifi on every request when the cache misses
        (which is the common case in tests).
        """
        try:
            from live.services.router import LiveDataRouter
        except Exception:  # pragma: no cover - defensive
            logger.exception('[Groups] LiveDataRouter unavailable.')
            return None

        try:
            router = LiveDataRouter()
            raw_groups = router.fdo.get_standings(router.world_cup_id)
        except Exception:  # pragma: no cover - defensive
            logger.exception('[Groups] FDO standings fetch failed.')
            return None

        if not raw_groups:
            return None

        # Pre-fetch every team referenced by the draw, indexed by
        # 3-letter code, to resolve FDO's TLA -> Team.
        codes = [c for codes in WORLD_CUP_2026_GROUPS.values() for c in codes]
        teams_by_code = {
            t.country_code: t
            for t in Team.objects.filter(country_code__in=codes)
        }
        snapshot = {}
        for raw in raw_groups:
            group_name = (raw.get('group') or '').strip()
            if not group_name:
                continue
            # FDO devolve o rotulo no formato "Group A", "Group B" ...
            # (com prefixo "Group " -- nao usar ``group_name[0]``, que
            # sempre seria "G"). Tomamos a ULTIMA palavra e o primeiro
            # caractere, cobrindo tanto "Group A" quanto casos futuros
            # como "Group A (UEFA)" ou somente "A".
            parts = group_name.split()
            letter = (parts[-1][0] if parts else '').upper()
            if letter not in WORLD_CUP_2026_GROUPS:
                continue
            per_team = {}
            for table in raw.get('table') or []:
                tla = (table.get('team') or {}).get('tla') or ''
                if tla not in teams_by_code:
                    continue
                per_team[teams_by_code[tla]] = {
                    'points': table.get('points', 0) or 0,
                    'played': table.get('playedGames', 0) or 0,
                    'won': table.get('won', 0) or 0,
                    'draw': table.get('draw', 0) or 0,
                    'lost': table.get('lost', 0) or 0,
                    'goals_for': table.get('goalsFor', 0) or 0,
                    'goals_against': table.get('goalsAgainst', 0) or 0,
                }
            snapshot[letter] = per_team
        return snapshot


class MatchBracketView(LoginRequiredMixin, TemplateView):
    """Render the knockout bracket (16-avos -> final).

    The 32 knockout matches are grouped by :class:`Round`, ordered
    by ``round.order``. The match for third place lives in a
    dedicated phase (``terceiro_lugar``) and is exposed separately
    so the template can render it as a stand-alone card below the
    semifinals.

    Matches whose ``home_team`` / ``away_team`` are the
    ``TBD-H`` / ``TBD-A`` placeholders (defined in the seed) are
    exposed as :class:`BracketMatch` dataclass-style dicts that
    flag them as "A definir" — the template can then render a
    neutral gray card without a country flag.
    """

    template_name = 'matches/match_bracket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        knockout_qs = (
            Match.objects
            .filter(round__phase__in=[
                'trinta_dois_avos',
                'oitavas',
                'quartas',
                'semi',
                'final',
            ])
            .select_related('home_team', 'away_team', 'stadium', 'round')
            .order_by('round__order', 'match_datetime')
        )
        # Group by round, preserving draw order.
        rounds_dict = {}
        for match in knockout_qs:
            r = match.round
            if r.pk not in rounds_dict:
                rounds_dict[r.pk] = {
                    'name': r.name,
                    'order': r.order,
                    'phase': r.phase,
                    'matches': [],
                }
            rounds_dict[r.pk]['matches'].append(match)
        context['rounds'] = sorted(
            rounds_dict.values(),
            key=lambda d: d['order'],
        )
        # Third place match is rendered as a stand-alone card.
        context['third_place_match'] = (
            Match.objects
            .filter(round__phase='terceiro_lugar')
            .select_related('home_team', 'away_team', 'stadium', 'round')
            .order_by('match_datetime')
            .first()
        )
        return context
