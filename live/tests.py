"""
Smoke tests for the live data clients and router.

The HTTP layer is patched so the tests do not hit the real APIs
(and do not consume the free-tier quotas).
"""

import io
import json
import unittest
from datetime import date as date_type
from datetime import datetime as datetime_type
from unittest import mock

from django.test import SimpleTestCase, TestCase, override_settings

from live.services.api_football import ApiFootballClient
from live.services.football_data_org import FootballDataOrgClient
from live.services.router import LiveDataRouter


# API-Football
AF_BASE_URL = 'https://v3.football.api-sports.io'
AF_FIXTURE_URL = '{0}/fixtures'.format(AF_BASE_URL)
AF_EVENTS_URL = '{0}/fixtures/events'.format(AF_BASE_URL)
AF_KEY = 'd44477e3b2d6ab2ddae8b6d5fa7207c6'

# football-data.org
FDO_BASE_URL = 'https://api.football-data.org/v4'
FDO_MATCH_URL = '{0}/matches'.format(FDO_BASE_URL)
FDO_COMPETITION_MATCHES_URL = '{0}/competitions/2000/matches'.format(FDO_BASE_URL)
FDO_STANDINGS_URL = '{0}/competitions/2000/standings'.format(FDO_BASE_URL)
FDO_KEY = 'fa7d6c4136794bbe97501e998edc0d63'


def _make_response(body, status=200):
    """Build a minimal file-like object with the ``status`` attribute."""
    raw = json.dumps(body).encode('utf-8') if not isinstance(
        body, bytes,
    ) else body
    response = io.BytesIO(raw)
    response.status = status
    return response


@override_settings(
    API_FOOTBALL_KEY=AF_KEY,
    API_FOOTBALL_BASE_URL=AF_BASE_URL,
    API_FOOTBALL_LEAGUE_ID=1,
    API_FOOTBALL_SEASON=2026,
)
class ApiFootballClientTests(SimpleTestCase):
    """Verify URL composition, headers and basic payload parsing."""

    def _assert_request(self, request, expected_url, expected_header):
        self.assertEqual(request.full_url, expected_url)
        headers = {
            name.lower(): value
            for name, value in request.header_items()
        }
        self.assertEqual(headers.get('x-apisports-key'), expected_header)
        self.assertEqual(headers.get('accept'), 'application/json')
        self.assertEqual(request.get_method(), 'GET')

    def test_get_fixture_builds_url_and_returns_first_item(self):
        payload = {'response': [{'fixture': {'id': 123}}]}
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response(payload),
        ) as urlopen:
            client = ApiFootballClient()
            result = client.get_fixture(123)

        self._assert_request(
            urlopen.call_args.args[0],
            '{0}?id=123'.format(AF_FIXTURE_URL),
            AF_KEY,
        )
        self.assertEqual(result, {'fixture': {'id': 123}})

    def test_get_fixtures_by_date_filters_by_league_and_season(self):
        payload = {'response': [{'fixture': {'id': 1}}, {'fixture': {'id': 2}}]}
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response(payload),
        ) as urlopen:
            client = ApiFootballClient()
            result = client.get_fixtures_by_date('2026-06-11')

        self._assert_request(
            urlopen.call_args.args[0],
            '{0}?date=2026-06-11&league=1&season=2026'.format(AF_FIXTURE_URL),
            AF_KEY,
        )
        self.assertEqual(len(result), 2)

    def test_get_fixture_events_returns_list(self):
        payload = {'response': [{'type': 'Goal'}]}
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response(payload),
        ) as urlopen:
            client = ApiFootballClient()
            result = client.get_fixture_events(456)

        self._assert_request(
            urlopen.call_args.args[0],
            '{0}?fixture=456'.format(AF_EVENTS_URL),
            AF_KEY,
        )
        self.assertEqual(result, [{'type': 'Goal'}])

    def test_get_fixture_returns_none_on_empty_response(self):
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response({'response': []}),
        ):
            self.assertIsNone(ApiFootballClient().get_fixture(999))

    def test_get_fixtures_by_date_returns_empty_list_on_http_error(self):
        with mock.patch(
            'urllib.request.urlopen',
            side_effect=OSError('boom'),
        ):
            self.assertEqual(
                ApiFootballClient().get_fixtures_by_date('2026-06-11'),
                [],
            )

    def test_get_fixture_returns_none_when_api_key_missing(self):
        with override_settings(API_FOOTBALL_KEY=''):
            self.assertIsNone(ApiFootballClient().get_fixture(1))


@override_settings(
    FOOTBALL_DATA_ORG_KEY=FDO_KEY,
    FOOTBALL_DATA_ORG_BASE_URL=FDO_BASE_URL,
    FOOTBALL_DATA_ORG_WORLD_CUP_ID=2000,
)
class FootballDataOrgClientTests(SimpleTestCase):
    """Verify URL composition, headers and basic payload parsing for FDO."""

    def _assert_request(self, request, expected_url, expected_header):
        self.assertEqual(request.full_url, expected_url)
        headers = {
            name.lower(): value
            for name, value in request.header_items()
        }
        self.assertEqual(headers.get('x-auth-token'), expected_header)
        self.assertEqual(headers.get('accept'), 'application/json')
        self.assertEqual(request.get_method(), 'GET')

    def test_get_match_builds_url_and_returns_payload(self):
        payload = {
            'id': 1,
            'utcDate': '2026-06-11T19:00:00Z',
            'homeTeam': {'name': 'Mexico'},
            'awayTeam': {'name': 'South Africa'},
        }
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response(payload),
        ) as urlopen:
            client = FootballDataOrgClient()
            result = client.get_match(1)

        self._assert_request(
            urlopen.call_args.args[0],
            '{0}/1'.format(FDO_MATCH_URL),
            FDO_KEY,
        )
        self.assertEqual(result, payload)

    def test_get_competition_matches_passes_date_range(self):
        payload = {
            'matches': [
                {
                    'id': 1,
                    'utcDate': '2026-06-11T19:00:00Z',
                    'homeTeam': {'name': 'Mexico'},
                    'awayTeam': {'name': 'South Africa'},
                },
            ],
        }
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response(payload),
        ) as urlopen:
            client = FootballDataOrgClient()
            result = client.get_competition_matches(
                2000, date_from='2026-06-11', date_to='2026-07-19',
            )

        self._assert_request(
            urlopen.call_args.args[0],
            '{0}?dateFrom=2026-06-11&dateTo=2026-07-19'.format(
                FDO_COMPETITION_MATCHES_URL,
            ),
            FDO_KEY,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 1)

    def test_get_competition_matches_without_dates_omits_query_string(self):
        payload = {'matches': []}
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response(payload),
        ) as urlopen:
            client = FootballDataOrgClient()
            result = client.get_competition_matches(2000)

        self._assert_request(
            urlopen.call_args.args[0],
            FDO_COMPETITION_MATCHES_URL,
            FDO_KEY,
        )
        self.assertEqual(result, [])

    def test_get_standings_returns_list(self):
        payload = {
            'standings': [
                {'stage': 'GROUP_A', 'table': []},
            ],
        }
        with mock.patch(
            'urllib.request.urlopen',
            return_value=_make_response(payload),
        ) as urlopen:
            client = FootballDataOrgClient()
            result = client.get_standings(2000)

        self._assert_request(
            urlopen.call_args.args[0],
            FDO_STANDINGS_URL,
            FDO_KEY,
        )
        self.assertEqual(result, [{'stage': 'GROUP_A', 'table': []}])

    def test_get_match_returns_none_on_http_error(self):
        with mock.patch(
            'urllib.request.urlopen',
            side_effect=OSError('boom'),
        ):
            self.assertIsNone(FootballDataOrgClient().get_match(1))

    def test_get_competition_matches_returns_empty_list_on_http_error(self):
        with mock.patch(
            'urllib.request.urlopen',
            side_effect=OSError('boom'),
        ):
            self.assertEqual(
                FootballDataOrgClient().get_competition_matches(2000),
                [],
            )

    def test_get_match_returns_none_when_api_key_missing(self):
        with override_settings(FOOTBALL_DATA_ORG_KEY=''):
            self.assertIsNone(FootballDataOrgClient().get_match(1))


class LiveDataRouterTests(SimpleTestCase):
    """Verify the router delegates to the right client and caches results."""

    def _fdo_payload(self):
        return [
            {
                'id': 1,
                'utcDate': '2026-06-11T19:00:00Z',
                'homeTeam': {'name': 'Mexico'},
                'awayTeam': {'name': 'South Africa'},
            },
            {
                'id': 2,
                'utcDate': '2026-06-12T19:00:00Z',
                'homeTeam': {'name': 'Canada'},
                'awayTeam': {'name': 'Bosnia and Herzegovina'},
            },
        ]

    def test_find_world_cup_match_uses_fdo_first(self):
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        fdo.get_competition_matches.return_value = self._fdo_payload()

        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )
        result = router.find_world_cup_match('2026-06-11', '2026-07-19')

        fdo.get_competition_matches.assert_called_once_with(
            2000, date_from='2026-06-11', date_to='2026-07-19',
        )
        af.get_fixtures_by_date.assert_not_called()
        self.assertEqual(len(result), 2)

    def test_find_world_cup_match_falls_back_to_api_football(self):
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        fdo.get_competition_matches.return_value = []
        af.get_fixtures_by_date.side_effect = [
            # Two days of calls. The router iterates from
            # 2026-06-11 to 2026-06-12 inclusive in this test.
            [
                {
                    'fixture': {'id': 99, 'date': '2026-06-11T19:00:00Z'},
                    'teams': {
                        'home': {'name': 'Mexico'},
                        'away': {'name': 'South Africa'},
                    },
                },
            ],
            [
                {
                    'fixture': {'id': 100, 'date': '2026-06-12T19:00:00Z'},
                    'teams': {
                        'home': {'name': 'Canada'},
                        'away': {'name': 'Bosnia and Herzegovina'},
                    },
                },
            ],
        ]

        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )
        result = router.find_world_cup_match('2026-06-11', '2026-06-12')

        fdo.get_competition_matches.assert_called_once()
        self.assertEqual(af.get_fixtures_by_date.call_count, 2)
        self.assertEqual(len(result), 2)

    def test_find_world_cup_match_caches_result(self):
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        fdo.get_competition_matches.return_value = self._fdo_payload()

        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )
        first = router.find_world_cup_match('2026-06-11', '2026-07-19')
        second = router.find_world_cup_match('2026-06-11', '2026-07-19')

        self.assertEqual(first, second)
        fdo.get_competition_matches.assert_called_once()
        af.get_fixtures_by_date.assert_not_called()

    def test_get_match_live_data_uses_fdo_first(self):
        fdo_match = {'id': 7, 'status': 'IN_PLAY'}
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        fdo.get_match.return_value = fdo_match

        match = mock.Mock(pk=1, external_id=7)
        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )
        result = router.get_match_live_data(match)

        fdo.get_match.assert_called_once_with(7)
        af.get_fixture.assert_not_called()
        self.assertEqual(result, fdo_match)

    def test_get_match_live_data_falls_back_to_api_football(self):
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        fdo.get_match.return_value = None
        af.get_fixture.return_value = {'fixture': {'id': 7}}

        match = mock.Mock(pk=1, external_id=7)
        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )
        result = router.get_match_live_data(match)

        fdo.get_match.assert_called_once_with(7)
        af.get_fixture.assert_called_once_with(7)
        self.assertEqual(result, {'fixture': {'id': 7}})

    def test_get_match_live_data_returns_none_without_external_id(self):
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )

        self.assertIsNone(router.get_match_live_data(mock.Mock(external_id=None)))
        fdo.get_match.assert_not_called()
        af.get_fixture.assert_not_called()

    def test_get_match_events_prefers_api_football(self):
        events = [{'type': 'Goal', 'detail': 'Neymar 45'}]
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        af.get_fixture_events.return_value = events

        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )
        result = router.get_match_events(mock.Mock(external_id=7))

        af.get_fixture_events.assert_called_once_with(7)
        fdo.get_match.assert_not_called()
        self.assertEqual(result, events)

    def test_get_match_events_falls_back_to_empty_list(self):
        fdo = mock.Mock(spec=FootballDataOrgClient)
        af = mock.Mock(spec=ApiFootballClient)
        af.get_fixture_events.return_value = []
        fdo.get_match.return_value = {'id': 7}

        router = LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )
        result = router.get_match_events(mock.Mock(external_id=7))

        self.assertEqual(result, [])

    def test_router_default_world_cup_id_uses_fdo_setting(self):
        fdo = mock.Mock(spec=FootballDataOrgClient)
        fdo.world_cup_id = 2000
        af = mock.Mock(spec=ApiFootballClient)
        fdo.get_competition_matches.return_value = []
        # The fallback path will iterate per-day through API-Football;
        # return an empty list on every call so the test only asserts
        # that the FDO call was made with the right competition id.
        af.get_fixtures_by_date.return_value = []

        with override_settings(FOOTBALL_DATA_ORG_WORLD_CUP_ID=2000):
            router = LiveDataRouter(fdo_client=fdo, api_football_client=af)
            router.find_world_cup_match('2026-06-11', '2026-06-12')

        fdo.get_competition_matches.assert_called_once_with(
            2000, date_from='2026-06-11', date_to='2026-06-12',
        )


class BackfillMatchExternalIdsTests(TestCase):
    """Cover the multi-variant matching added for US-7.2.

    The fixtures below deliberately use pt-BR names on the local side
    (the same as the seeder) and English names on the FDO side, so the
    only way for the matcher to succeed is by consulting ``name_en``
    (and falling back to ``country_code`` when needed).
    """

    def _make_match(self, home, away, dt, external_id=None):
        """Helper: build a Match with a fake home/away team and stadium."""
        from matches.models import Match, Round, Stadium, Team

        stadium, _ = Stadium.objects.get_or_create(
            name='Test Stadium',
            defaults={'city': 'TC', 'country': 'TC', 'capacity': 1},
        )
        round_, _ = Round.objects.get_or_create(
            name='Test Round',
            defaults={'order': 99, 'phase': 'grupo'},
        )
        home_team, _ = Team.objects.update_or_create(
            country_code=home['country_code'],
            defaults={
                'name': home['name'],
                'name_en': home.get('name_en', ''),
                'confederation': home.get('confederation', 'UEFA'),
                'flag_emoji': '',
            },
        )
        away_team, _ = Team.objects.update_or_create(
            country_code=away['country_code'],
            defaults={
                'name': away['name'],
                'name_en': away.get('name_en', ''),
                'confederation': away.get('confederation', 'UEFA'),
                'flag_emoji': '',
            },
        )
        return Match.objects.create(
            round=round_,
            stadium=stadium,
            home_team=home_team,
            away_team=away_team,
            match_datetime=dt,
            external_id=external_id,
        )

    def _run_command(self, source='[FDO]'):
        from io import StringIO
        from django.core.management import call_command

        from live.management.commands.backfill_match_external_ids import Command

        out = StringIO()
        cmd = Command()
        cmd.stdout = out
        # Build a router-like stub that bypasses the network entirely.
        router = mock.Mock()
        # The command inspects ``router._cache`` to detect the source.
        router._cache = {
            ('find_world_cup_match', '2026-06-11', '2026-06-12'): self._fdo_payload,
        }
        router.find_world_cup_match.return_value = self._fdo_payload
        with mock.patch(
            'live.management.commands.backfill_match_external_ids.LiveDataRouter',
            return_value=router,
        ):
            cmd.handle(
                **{},
                **{'no_input': True, 'dry_run': False, 'date_from': '2026-06-11', 'date_to': '2026-06-12'},
            )
        return out.getvalue()

    def setUp(self):
        self._fdo_payload = [
            {
                'id': 1,
                'utcDate': '2026-06-11T19:00:00Z',
                'homeTeam': {'name': 'South Korea', 'tla': 'KOR'},
                'awayTeam': {'name': 'Czechia', 'tla': 'CZE'},
            },
            {
                'id': 2,
                'utcDate': '2026-06-12T19:00:00Z',
                'homeTeam': {'name': 'Morocco', 'tla': 'MAR'},
                'awayTeam': {'name': 'Bosnia-Herzegovina', 'tla': 'BIH'},
            },
            {
                'id': 3,
                'utcDate': '2026-06-12T22:00:00Z',
                'homeTeam': {'name': 'United States', 'tla': 'USA'},
                'awayTeam': {'name': 'Paraguay', 'tla': 'PAR'},
            },
        ]

    def test_candidate_keys_prefer_pt_name_then_en_then_tla(self):
        from matches.models import Team
        t = Team(
            name='Franca',
            name_en='France',
            country_code='FRA',
        )
        from live.management.commands.backfill_match_external_ids import (
            Command as BackfillCommand,
        )
        cands = BackfillCommand()._candidate_keys(t)
        self.assertEqual(cands, ['franca', 'france', 'fra'])

    def test_candidate_keys_skip_empty_fields(self):
        from matches.models import Team
        # Simulates a TBD placeholder: name_en is blank, code is TBD-H.
        t = Team(
            name='A definir (mandante)',
            name_en='',
            country_code='TBD-H',
        )
        from live.management.commands.backfill_match_external_ids import (
            Command as BackfillCommand,
        )
        cands = BackfillCommand()._candidate_keys(t)
        # 'TBD-H' normalized to 'tbdh' is still a candidate, but if we
        # had wanted to exclude TBDs we'd just not call the function.
        # The important assertion is that name_en did not contribute.
        self.assertNotIn('', cands)
        self.assertIn('adefinirmandante', cands)

    def test_find_fixture_matches_by_name_en(self):
        from live.management.commands.backfill_match_external_ids import (
            Command as BackfillCommand,
        )
        cmd = BackfillCommand()
        # Local match uses pt-BR; upstream uses English.
        match = self._make_match(
            home={'name': 'Coreia do Sul', 'name_en': 'South Korea', 'country_code': 'KOR'},
            away={'name': 'Chequia', 'name_en': 'Czechia', 'country_code': 'CZE'},
            dt=datetime_type(2026, 6, 11, 19, 0),
        )
        from collections import defaultdict
        # Reuse the production indexer: it inserts the primary (name) key
        # plus the TLA key.
        fixture_index, _ = cmd._index_upstream(
            cmd._parse_fixture(f, '[FDO]') and [f] for f in self._fdo_payload
        ) if False else (defaultdict(dict), 0)
        # Manually index the payload (avoids relying on the private
        # chain above).
        for f in self._fdo_payload:
            parsed = cmd._parse_fixture(f, '[FDO]')
            if parsed is None:
                continue
            md, h, a, ht, at = parsed
            fixture_index[md][(h, a)] = f
            if ht and at:
                fixture_index[md].setdefault((ht, at), f)

        fixtures = fixture_index[date_type(2026, 6, 11)]
        fixture, inverted, label = cmd._find_fixture(match, fixtures)
        self.assertIsNotNone(fixture)
        self.assertFalse(inverted)
        self.assertIn('South Korea', label)
        self.assertEqual(cmd._extract_external_id(fixture, '[FDO]'), 1)

    def test_find_fixture_matches_by_country_code_when_names_fail(self):
        from live.management.commands.backfill_match_external_ids import (
            Command as BackfillCommand,
        )
        cmd = BackfillCommand()
        # Names diverge in every field; the only common key is the TLA.
        match = self._make_match(
            home={'name': 'Desconhecido A', 'name_en': 'Desconhecido A', 'country_code': 'MAR'},
            away={'name': 'Desconhecido B', 'name_en': 'Desconhecido B', 'country_code': 'BIH'},
            dt=datetime_type(2026, 6, 12, 19, 0),
        )
        from collections import defaultdict
        fixture_index = defaultdict(dict)
        for f in self._fdo_payload:
            parsed = cmd._parse_fixture(f, '[FDO]')
            if parsed is None:
                continue
            md, h, a, ht, at = parsed
            fixture_index[md][(h, a)] = f
            if ht and at:
                fixture_index[md].setdefault((ht, at), f)
        fixtures = fixture_index[date_type(2026, 6, 12)]
        fixture, inverted, label = cmd._find_fixture(match, fixtures)
        self.assertIsNotNone(fixture)
        self.assertEqual(cmd._extract_external_id(fixture, '[FDO]'), 2)
        self.assertIn('MAR', label)
        self.assertIn('BIH', label)

    def test_find_fixture_returns_none_for_tbd(self):
        from live.management.commands.backfill_match_external_ids import (
            Command as BackfillCommand,
        )
        cmd = BackfillCommand()
        match = self._make_match(
            home={'name': 'A definir (mandante)', 'name_en': '', 'country_code': 'TBD-H'},
            away={'name': 'A definir (visitante)', 'name_en': '', 'country_code': 'TBD-A'},
            dt=datetime_type(2026, 6, 15, 19, 0),
        )
        from collections import defaultdict
        fixture_index = defaultdict(dict)
        for f in self._fdo_payload:
            parsed = cmd._parse_fixture(f, '[FDO]')
            if parsed is None:
                continue
            md, h, a, ht, at = parsed
            fixture_index[md][(h, a)] = f
        fixtures = fixture_index[date_type(2026, 6, 15)]
        fixture, inverted, label = cmd._find_fixture(match, fixtures)
        self.assertIsNone(fixture)
        self.assertEqual(inverted, False)
        self.assertEqual(label, '')


class MatchSyncViewTests(TestCase):
    """Smoke tests for the ``MatchSyncView`` endpoint.

    The router is mocked so the tests stay offline and deterministic.
    """

    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.core.cache import cache
        from matches.models import Match, Round, Stadium, Team

        User = get_user_model()
        self.user = User.objects.create_user(
            email='sync@example.com', password='x',
        )
        # ``self.client`` is created per-test by Django's TestCase; we
        # need to log the user in here so authenticated-only assertions
        # can be exercised.
        self.client.force_login(self.user)

        self.stadium, _ = Stadium.objects.get_or_create(
            name='Sync Stadium',
            defaults={'city': 'SC', 'country': 'SC', 'capacity': 1},
        )
        self.round_, _ = Round.objects.get_or_create(
            name='Sync Round',
            defaults={'order': 1, 'phase': 'grupo'},
        )
        self.home, _ = Team.objects.get_or_create(
            country_code='HOM',
            defaults={'name': 'Home', 'confederation': 'UEFA'},
        )
        self.away, _ = Team.objects.get_or_create(
            country_code='AWA',
            defaults={'name': 'Away', 'confederation': 'UEFA'},
        )
        self.match = Match.objects.create(
            round=self.round_,
            stadium=self.stadium,
            home_team=self.home,
            away_team=self.away,
            match_datetime=datetime_type(2026, 6, 11, 19, 0),
            external_id=4242,
        )
        # Make sure the rate-limit cache doesn't leak between tests.
        cache.clear()

    def test_post_calls_sync_match_from_api(self):
        """The view delegates to ``sync_match_from_api`` for valid matches."""
        from django.urls import reverse

        from live.services.sync import SyncResult

        with mock.patch(
            'live.views.sync_match_from_api',
        ) as sync_mock:
            sync_mock.return_value = SyncResult(
                success=True, status_changed=False, events_synced=0,
            )
            response = self.client.post(
                reverse('match_sync', args=[self.match.pk]),
            )

        sync_mock.assert_called_once()
        # First positional arg is the Match instance.
        self.assertEqual(sync_mock.call_args.args[0].pk, self.match.pk)
        # Successful sync redirects somewhere (referer or match_list).
        self.assertEqual(response.status_code, 302)

    def test_post_requires_login(self):
        from django.urls import reverse

        self.client.logout()
        response = self.client.post(
            reverse('match_sync', args=[self.match.pk]),
        )
        # LoginRequiredMixin redirects to LOGIN_URL when unauthenticated.
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_post_rejects_get(self):
        from django.urls import reverse

        response = self.client.get(
            reverse('match_sync', args=[self.match.pk]),
        )
        self.assertEqual(response.status_code, 405)

    def test_post_without_external_id_does_not_call_sync(self):
        from django.urls import reverse

        self.match.external_id = None
        self.match.save()

        with mock.patch('live.views.sync_match_from_api') as sync_mock:
            response = self.client.post(
                reverse('match_sync', args=[self.match.pk]),
            )

        sync_mock.assert_not_called()
        self.assertEqual(response.status_code, 302)


class MatchCardPartialViewTests(TestCase):
    """Smoke tests for the polling endpoint of US-7.4.

    The view is the payload side of the JS polling that runs every
    60s for cards with ``data-live="1"``. It must:

    * require authentication (unauthenticated requests redirect);
    * return the rendered ``match_card.html`` partial (200) for an
      existing match;
    * include the article wrapper with the ``data-match-id`` and
      ``data-live`` attributes that the client-side script keys off;
    * flip ``data-live`` to ``"0"`` for any non-live match;
    * 404 for a missing match (so a stale id is a clean failure).
    """

    def setUp(self):
        from django.contrib.auth import get_user_model
        from matches.models import Match, Round, Stadium, Team

        User = get_user_model()
        self.user = User.objects.create_user(
            email='partial@example.com', password='x',
        )
        self.client.force_login(self.user)

        self.stadium, _ = Stadium.objects.get_or_create(
            name='Partial Stadium',
            defaults={'city': 'PC', 'country': 'PC', 'capacity': 1},
        )
        self.round_, _ = Round.objects.get_or_create(
            name='Partial Round',
            defaults={'order': 1, 'phase': 'grupo'},
        )
        self.home, _ = Team.objects.get_or_create(
            country_code='HOP',
            defaults={'name': 'HomeP', 'confederation': 'UEFA'},
        )
        self.away, _ = Team.objects.get_or_create(
            country_code='AWP',
            defaults={'name': 'AwayP', 'confederation': 'UEFA'},
        )
        # ``Match`` is imported in setUp so the helper method below
        # can reference it via ``self.Match`` (instance attribute,
        # not class-level). Importing at the top of the file would
        # shadow the helper method's local namespace and break.
        self.Match = Match

    def _make_match(self, **overrides):
        defaults = {
            'round': self.round_,
            'stadium': self.stadium,
            'home_team': self.home,
            'away_team': self.away,
            'match_datetime': datetime_type(2026, 6, 11, 19, 0),
        }
        defaults.update(overrides)
        return self.Match.objects.create(**defaults)

    def test_get_returns_200_and_renders_partial(self):
        from django.urls import reverse

        match = self._make_match()
        response = self.client.get(
            reverse('match_card_partial', args=[match.pk]),
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        # The partial renders the article wrapper that the
        # client-side polling script keys off.
        self.assertIn("data-match-id='{0}'".format(match.pk), body)
        # No live game in the test fixtures -> data-live="0".
        self.assertIn("data-live='0'", body)
        # Placar placeholder para jogos sem placar registrado.
        self.assertIn('&middot;', body)

    def test_get_marks_live_match_with_data_live_1(self):
        from django.urls import reverse

        match = self._make_match(status='em_andamento', elapsed_minute=42)
        response = self.client.get(
            reverse('match_card_partial', args=[match.pk]),
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        self.assertIn("data-live='1'", body)
        # O badge AO VIVO aparece e mostra o minuto decorrido.
        self.assertIn('AO VIVO', body)
        self.assertIn("42'", body)

    def test_get_renders_penalty_score_when_present(self):
        from django.urls import reverse

        match = self._make_match(
            status='finalizado',
            home_score=1,
            away_score=1,
            penalties_home=4,
            penalties_away=3,
        )
        response = self.client.get(
            reverse('match_card_partial', args=[match.pk]),
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        self.assertIn('penaltis', body)
        # Numeros de penaltis convertidos aparecem dentro do card.
        self.assertIn('>4<', body)
        self.assertIn('>3<', body)

    def test_get_requires_login(self):
        from django.urls import reverse

        match = self._make_match()
        self.client.logout()
        response = self.client.get(
            reverse('match_card_partial', args=[match.pk]),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_get_404_for_missing_match(self):
        from django.urls import reverse

        response = self.client.get(
            reverse('match_card_partial', args=[999999]),
        )
        self.assertEqual(response.status_code, 404)


# ----------------------------------------------------------------------
# US-7.5: MatchEvent model + sync of events from API-Football + UI partial
# ----------------------------------------------------------------------

class MatchEventModelTests(TestCase):
    """Cover the ``MatchEvent`` model basics: __str__ and ordering."""

    def setUp(self):
        from matches.models import Match, Round, Stadium, Team

        self.stadium, _ = Stadium.objects.get_or_create(
            name='Event Stadium',
            defaults={'city': 'EC', 'country': 'EC', 'capacity': 1},
        )
        self.round_, _ = Round.objects.get_or_create(
            name='Event Round',
            defaults={'order': 1, 'phase': 'grupo'},
        )
        self.home, _ = Team.objects.get_or_create(
            country_code='HME',
            defaults={'name': 'HomeE', 'name_en': 'HomeE', 'confederation': 'UEFA'},
        )
        self.away, _ = Team.objects.get_or_create(
            country_code='AWE',
            defaults={'name': 'AwayE', 'name_en': 'AwayE', 'confederation': 'UEFA'},
        )
        self.match = Match.objects.create(
            round=self.round_,
            stadium=self.stadium,
            home_team=self.home,
            away_team=self.away,
            match_datetime=datetime_type(2026, 6, 11, 19, 0),
        )

    def _make_event(self, **overrides):
        from live.models import MatchEvent

        defaults = {
            'match': self.match,
            'minute': 30,
            'type': 'goal',
            'team': self.home,
            'player': 'Neymar',
            'assist_player': 'Vinicius',
        }
        defaults.update(overrides)
        return MatchEvent.objects.create(**defaults)

    def test_str_includes_minute_type_player_and_team(self):
        event = self._make_event()
        # __str__ = "<minute>' <type display> <player> (<team>)"
        rendered = str(event)
        self.assertIn("30'", rendered)
        self.assertIn('Gol', rendered)
        self.assertIn('Neymar', rendered)
        self.assertIn(str(self.home), rendered)

    def test_default_ordering_is_by_minute_then_id(self):
        later = self._make_event(minute=80, player='Late')
        earlier = self._make_event(minute=10, player='Early')
        same_minute_first = self._make_event(minute=30, player='FirstAt30')
        same_minute_second = self._make_event(minute=30, player='SecondAt30')

        events = list(self.match.events.all())
        # The default ordering on ``MatchEvent.Meta`` is
        # ``(minute, id)`` so the two 30' events come in insertion
        # order and 10' precedes 80'.
        self.assertEqual(
            [e.pk for e in events],
            [earlier.pk, same_minute_first.pk, same_minute_second.pk, later.pk],
        )


class SyncMatchEventsTests(TestCase):
    """US-7.5 sync of in-match events from the API-Football payload.

    The router is mocked so the tests stay offline and deterministic.
    A small fake ``ApiFootballClient`` is plugged in to return exactly
    the event list we want to exercise.
    """

    def setUp(self):
        from matches.models import Match, Round, Stadium, Team

        self.stadium, _ = Stadium.objects.get_or_create(
            name='SyncEv Stadium',
            defaults={'city': 'SE', 'country': 'SE', 'capacity': 1},
        )
        self.round_, _ = Round.objects.get_or_create(
            name='SyncEv Round',
            defaults={'order': 1, 'phase': 'grupo'},
        )
        # Teams are stored with English ``name_en`` so the sync can
        # resolve them by the English name the API exposes.
        self.home, _ = Team.objects.get_or_create(
            country_code='HE1',
            defaults={
                'name': 'Brasil', 'name_en': 'Brazil',
                'confederation': 'CONMEBOL',
            },
        )
        self.away, _ = Team.objects.get_or_create(
            country_code='AE1',
            defaults={
                'name': 'Franca', 'name_en': 'France',
                'confederation': 'UEFA',
            },
        )
        self.match = Match.objects.create(
            round=self.round_,
            stadium=self.stadium,
            home_team=self.home,
            away_team=self.away,
            match_datetime=datetime_type(2026, 6, 11, 19, 0),
            external_id=987,
        )
        # The ``MatchSyncView``-side cache must be empty so the rate
        # limit does not leak into these tests.
        from django.core.cache import cache
        cache.clear()

    def _build_router(self, af_payload, fdo_payload=None):
        """Wire up a LiveDataRouter with mocked clients."""
        fdo = mock.Mock(spec=FootballDataOrgClient)
        fdo.world_cup_id = 2000
        af = mock.Mock(spec=ApiFootballClient)
        af.get_fixture_events.return_value = af_payload
        # The score/status side of the sync needs a get_fixture() call
        # too. Hand it back a minimal "this is a finished match"
        # payload so the sync does not bail out.
        fdo.get_match.return_value = None
        af.get_fixture.return_value = {
            'fixture': {
                'id': 987,
                'status': {'short': 'FT', 'elapsed': 90},
            },
            'goals': {'home': 1, 'away': 0},
            'teams': {
                'home': {'id': 1, 'name': 'Brazil'},
                'away': {'id': 2, 'name': 'France'},
            },
        }
        return LiveDataRouter(
            fdo_client=fdo, api_football_client=af, world_cup_id=2000,
        )

    def test_sync_with_one_goal_creates_one_event(self):
        from live.models import MatchEvent
        from live.services.sync import sync_match_from_api

        af_payload = [
            {
                'time': {'elapsed': 45},
                'team': {'id': 1, 'name': 'Brazil'},
                'player': {'id': 99, 'name': 'Neymar'},
                'assist': {'id': 100, 'name': 'Vinicius Jr'},
                'type': 'Goal',
                'detail': 'Normal Goal',
            },
        ]
        router = self._build_router(af_payload)
        result = sync_match_from_api(self.match, router=router)

        self.assertTrue(result.success)
        self.assertEqual(result.events_synced, 1)
        events = list(MatchEvent.objects.filter(match=self.match))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].type, 'goal')
        self.assertEqual(events[0].player, 'Neymar')
        self.assertEqual(events[0].team, self.home)
        self.assertEqual(events[0].assist_player, 'Vinicius Jr')
        self.assertEqual(events[0].minute, 45)

    def test_sync_with_yellow_card_creates_event_with_type_yellow(self):
        from live.models import MatchEvent
        from live.services.sync import sync_match_from_api

        af_payload = [
            {
                'time': {'elapsed': 30},
                'team': {'id': 1, 'name': 'Brazil'},
                'player': {'id': 7, 'name': 'Casemiro'},
                'type': 'Card',
                'detail': 'Yellow Card',
            },
        ]
        router = self._build_router(af_payload)
        result = sync_match_from_api(self.match, router=router)

        self.assertTrue(result.success)
        self.assertEqual(result.events_synced, 1)
        event = MatchEvent.objects.get(match=self.match)
        self.assertEqual(event.type, 'yellow_card')
        self.assertEqual(event.player, 'Casemiro')
        self.assertEqual(event.minute, 30)
        self.assertEqual(event.assist_player, '')

    def test_sync_without_external_id_creates_no_events(self):
        from live.models import MatchEvent
        from live.services.sync import sync_match_from_api

        self.match.external_id = None
        self.match.save()
        # No router needed; the no-external-id branch short-circuits.
        result = sync_match_from_api(self.match)

        self.assertFalse(result.success)
        self.assertEqual(result.events_synced, 0)
        self.assertEqual(MatchEvent.objects.filter(match=self.match).count(), 0)

    def test_sync_with_substitution_splits_into_in_and_out(self):
        from live.models import MatchEvent
        from live.services.sync import sync_match_from_api

        af_payload = [
            {
                'time': {'elapsed': 65},
                'team': {'id': 1, 'name': 'Brazil'},
                'player': {'id': 11, 'name': 'Raphinha'},
                'assist': {'id': 19, 'name': 'Antony'},
                'type': 'Subst',
                'detail': 'Substitution 1',
            },
        ]
        router = self._build_router(af_payload)
        result = sync_match_from_api(self.match, router=router)

        self.assertTrue(result.success)
        # A single Subst row maps to two MatchEvent rows (in + out).
        self.assertEqual(result.events_synced, 2)
        events = list(
            MatchEvent.objects.filter(match=self.match).order_by('type'),
        )
        self.assertEqual(len(events), 2)
        types = {e.type for e in events}
        self.assertEqual(types, {'substitution_in', 'substitution_out'})
        # The OUT player is in player.name; the IN player is in
        # assist.name.
        out_event = next(e for e in events if e.type == 'substitution_out')
        in_event = next(e for e in events if e.type == 'substitution_in')
        self.assertEqual(out_event.player, 'Raphinha')
        self.assertEqual(in_event.player, 'Antony')


class MatchCardPartialEventsTests(TestCase):
    """Verify the events list is rendered inside the card partial.

    The endpoint is the same ``MatchCardPartialView`` polled by the
    60s script of US-7.4 — we just need to confirm that, for a match
    with events, the response body includes the expected markers.
    """

    def setUp(self):
        from matches.models import Match, Round, Stadium, Team
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_user(
            email='partial-events@example.com', password='x',
        )
        self.client.force_login(self.user)

        self.stadium, _ = Stadium.objects.get_or_create(
            name='PE Stadium',
            defaults={'city': 'PE', 'country': 'PE', 'capacity': 1},
        )
        self.round_, _ = Round.objects.get_or_create(
            name='PE Round',
            defaults={'order': 1, 'phase': 'grupo'},
        )
        self.home, _ = Team.objects.get_or_create(
            country_code='HE2',
            defaults={
                'name': 'Brasil', 'name_en': 'Brazil',
                'confederation': 'CONMEBOL',
            },
        )
        self.away, _ = Team.objects.get_or_create(
            country_code='AE2',
            defaults={
                'name': 'Franca', 'name_en': 'France',
                'confederation': 'UEFA',
            },
        )
        self.match = Match.objects.create(
            round=self.round_,
            stadium=self.stadium,
            home_team=self.home,
            away_team=self.away,
            match_datetime=datetime_type(2026, 6, 11, 19, 0),
            status='finalizado',
        )

    def test_partial_renders_event_lines(self):
        from django.urls import reverse
        from live.models import MatchEvent

        MatchEvent.objects.create(
            match=self.match,
            minute=45,
            type='goal',
            team=self.home,
            player='Neymar',
            assist_player='Vinicius',
        )
        MatchEvent.objects.create(
            match=self.match,
            minute=30,
            type='yellow_card',
            team=self.away,
            player='Mbappe',
            assist_player='',
        )

        response = self.client.get(
            reverse('match_card_partial', args=[self.match.pk]),
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')

        # Goal line: minute, soccer ball, player, assist.
        self.assertIn("45'", body)
        self.assertIn('Neymar', body)
        self.assertIn('Vinicius', body)
        # Yellow card line.
        self.assertIn("30'", body)
        self.assertIn('Mbappe', body)
        # The yellow card uses the emoji icon; the goal uses a soccer
        # ball. Both unicode characters should appear in the body.
        self.assertIn('\u26bd', body)  # goal emoji (soccer ball)

    def test_partial_renders_empty_state_when_no_events(self):
        from django.urls import reverse

        response = self.client.get(
            reverse('match_card_partial', args=[self.match.pk]),
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode('utf-8')
        self.assertIn('Nenhum evento registrado.', body)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
