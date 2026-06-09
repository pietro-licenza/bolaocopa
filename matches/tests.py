"""
Tests for the US-7.7 dedicated "Jogos" sub-views.

These tests are intentionally light: they only verify the *contract*
of the new views (route resolution + key context keys) so they can
be added without spinning up 48 teams, 16 stadiums and 104 matches.

The point-calculation logic for finished matches (the part that
actually updates the standings) is exercised by the signal tests
in ``matches.tests`` (signal suite is part of US-5.2 / US-7.4). The
``MatchGroupsView`` is a pure consumer of that data — we trust the
calculation and only check the structural pieces here.
"""

import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from matches.groups_data import (
    WORLD_CUP_2026_GROUPS,
    get_all_groups,
    get_group_for_team,
)
from matches.models import Match, Round, Stadium, Team


User = get_user_model()


def _make_team(code, name):
    return Team.objects.create(
        name=name,
        name_en=name,
        country_code=code,
        flag_emoji='',
    )


def _make_round(name, order, phase):
    return Round.objects.create(name=name, order=order, phase=phase)


def _make_stadium(name='Estadio X'):
    return Stadium.objects.create(
        name=name,
        city='Cidade X',
        country='Pais X',
        capacity=40000,
    )


class GroupsDataTests(TestCase):
    """Static data sanity: every group has 4 teams, all 12 groups exist."""

    def test_all_twelve_groups_present(self):
        self.assertEqual(get_all_groups(), list('ABCDEFGHIJKL'))

    def test_each_group_has_four_teams(self):
        for letter, codes in WORLD_CUP_2026_GROUPS.items():
            with self.subTest(group=letter):
                self.assertEqual(len(codes), 4, f'Group {letter} != 4 teams')

    def test_total_team_count(self):
        all_codes = [c for codes in WORLD_CUP_2026_GROUPS.values() for c in codes]
        self.assertEqual(len(all_codes), 48)

    def test_get_group_for_team(self):
        self.assertEqual(get_group_for_team('BRA'), 'C')
        self.assertEqual(get_group_for_team('ARG'), 'J')
        self.assertIsNone(get_group_for_team('TBD-H'))
        self.assertIsNone(get_group_for_team(None))
        self.assertIsNone(get_group_for_team(''))


class MatchHomeViewTests(TestCase):
    """The ``/matches/`` landing page returns 200 and the 3 sub-links."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='home@example.com',
            password='pass-test-123',
        )
        self.client.force_login(self.user)

    def test_match_home_returns_200(self):
        response = self.client.get(reverse('match_home'))
        self.assertEqual(response.status_code, 200)

    def test_match_home_exposes_three_sub_links(self):
        response = self.client.get(reverse('match_home'))
        self.assertEqual(response.status_code, 200)
        sub_links = response.context['sub_links']
        self.assertEqual(len(sub_links), 3)
        labels = {link['label'] for link in sub_links}
        self.assertEqual(labels, {'Agenda', 'Grupos', 'Chaveamento'})

    def test_match_home_redirects_anonymous_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('match_home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])


class MatchScheduleViewTests(TestCase):
    """``/matches/schedule/`` lists matches of the selected day."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='sched@example.com',
            password='pass-test-123',
        )
        self.client.force_login(self.user)
        self.round_group = _make_round('Fase de Grupos', 1, 'grupo')
        self.stadium = _make_stadium()
        self.team_a = _make_team('AAA', 'Time A')
        self.team_b = _make_team('BBB', 'Time B')
        self.team_c = _make_team('CCC', 'Time C')
        self.team_d = _make_team('DDD', 'Time D')

    def _match(self, dt, home, away):
        return Match.objects.create(
            round=self.round_group,
            stadium=self.stadium,
            home_team=home,
            away_team=away,
            match_datetime=dt,
        )

    def test_default_schedule_renders_today(self):
        """No kwargs / query params → renders today (any number of matches)."""
        response = self.client.get(reverse('match_schedule'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['selected_date'],
            timezone.localdate(),
        )
        # available_dates is present and is a list
        self.assertIsInstance(response.context['available_dates'], list)

    def test_schedule_with_date_filters_correctly(self):
        """A date kwarg narrows the queryset to that day's matches."""
        target = datetime.date(2026, 6, 15)
        dt_in = timezone.make_aware(
            datetime.datetime(2026, 6, 15, 16, 0),
        )
        dt_out = timezone.make_aware(
            datetime.datetime(2026, 6, 16, 16, 0),
        )
        self._match(dt_in, self.team_a, self.team_b)
        self._match(dt_out, self.team_c, self.team_d)

        response = self.client.get(
            reverse('match_schedule'),
            {'date': '2026-06-15'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_date'], target)
        rendered = list(response.context['matches'])
        self.assertEqual(len(rendered), 1)
        self.assertEqual(rendered[0].home_team, self.team_a)

    def test_schedule_with_url_date_kwarg(self):
        """``/matches/schedule/2026-06-15/`` (URL kwarg) is honoured."""
        dt = timezone.make_aware(datetime.datetime(2026, 6, 15, 16, 0))
        self._match(dt, self.team_a, self.team_b)
        response = self.client.get('/matches/schedule/2026-06-15/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(response.context['matches'])), 1)


class MatchGroupsViewTests(TestCase):
    """``/matches/groups/`` returns 200 and the 12-group context."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='groups@example.com',
            password='pass-test-123',
        )
        self.client.force_login(self.user)

    def test_match_groups_returns_200(self):
        with mock.patch(
            'matches.views.MatchGroupsView._get_fdo_snapshot',
            return_value=None,
        ):
            response = self.client.get(reverse('match_groups'))
        self.assertEqual(response.status_code, 200)

    def test_match_groups_exposes_twelve_groups(self):
        with mock.patch(
            'matches.views.MatchGroupsView._get_fdo_snapshot',
            return_value=None,
        ):
            response = self.client.get(reverse('match_groups'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['groups'].keys()), set('ABCDEFGHIJKL'))
        self.assertEqual(response.context['group_letters'], list('ABCDEFGHIJKL'))
        # Each group has a list (possibly empty) under standings
        for letter in 'ABCDEFGHIJKL':
            with self.subTest(group=letter):
                self.assertIn(letter, response.context['standings'])
                self.assertIsInstance(response.context['standings'][letter], list)

    def test_match_groups_computes_local_standings_for_finished_matches(self):
        """A single finished match contributes 3 pts to the winner."""
        with mock.patch(
            'matches.views.MatchGroupsView._get_fdo_snapshot',
            return_value=None,
        ):
            # We only seed two of the four group-A teams; the test
            # only cares about the calculation, not the roster.
            mexico = _make_team('MEX', 'Mexico')
            rsa = _make_team('RSA', 'South Africa')
            round_group = _make_round('Fase de Grupos', 1, 'grupo')
            stadium = _make_stadium()
            Match.objects.create(
                round=round_group,
                stadium=stadium,
                home_team=mexico,
                away_team=rsa,
                match_datetime=timezone.now(),
                home_score=2,
                away_score=0,
                status='finalizado',
            )
            response = self.client.get(reverse('match_groups'))
            self.assertEqual(response.status_code, 200)
            standings = response.context['standings']
            # Exactly the two teams we created show up in group A.
            self.assertEqual(len(standings['A']), 2)
            mexico_row = next(
                r for r in standings['A'] if r['team'] == mexico
            )
            rsa_row = next(
                r for r in standings['A'] if r['team'] == rsa
            )
            # Mexico won 2-0 → 3 pts, 1 V, GP=2, GC=0, SG=+2.
            self.assertEqual(mexico_row['P'], 3)
            self.assertEqual(mexico_row['V'], 1)
            self.assertEqual(mexico_row['D'], 0)
            self.assertEqual(mexico_row['GP'], 2)
            self.assertEqual(mexico_row['GC'], 0)
            self.assertEqual(mexico_row['SG'], 2)
            # South Africa lost 0-2 → 0 pts, 1 D, GP=0, GC=2, SG=-2.
            self.assertEqual(rsa_row['P'], 0)
            self.assertEqual(rsa_row['D'], 1)
            self.assertEqual(rsa_row['GP'], 0)
            self.assertEqual(rsa_row['GC'], 2)
            self.assertEqual(rsa_row['SG'], -2)
            # Mexico is ranked above South Africa.
            self.assertEqual(mexico_row['position'], 1)
            self.assertEqual(rsa_row['position'], 2)


class MatchBracketViewTests(TestCase):
    """``/matches/bracket/`` returns 200 and groups by round."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='bracket@example.com',
            password='pass-test-123',
        )
        self.client.force_login(self.user)
        # Make sure all 5 knockout phase rounds exist.
        self.round_32 = _make_round('16-avos de Final', 2, 'trinta_dois_avos')
        self.round_16 = _make_round('Oitavas de Final', 3, 'oitavas')
        self.round_8 = _make_round('Quartas de Final', 4, 'quartas')
        self.round_semi = _make_round('Semifinal', 5, 'semi')
        self.round_3rd = _make_round('Disputa de 3o Lugar', 6, 'terceiro_lugar')
        self.round_final = _make_round('Final', 7, 'final')
        self.stadium = _make_stadium()
        self.team_a = _make_team('T1', 'Time 1')
        self.team_b = _make_team('T2', 'Time 2')
        # The TBD placeholders live in the real DB because of the
        # seed command, but the test database is fresh — recreate
        # them here.
        self.tbd_h, _ = Team.objects.get_or_create(
            country_code='TBD-H',
            defaults={'name': 'A definir (mandante)', 'name_en': 'TBD Home'},
        )
        self.tbd_a, _ = Team.objects.get_or_create(
            country_code='TBD-A',
            defaults={'name': 'A definir (visitante)', 'name_en': 'TBD Away'},
        )

    def test_match_bracket_returns_200(self):
        response = self.client.get(reverse('match_bracket'))
        self.assertEqual(response.status_code, 200)

    def test_match_bracket_groups_rounds_and_third_place(self):
        # Add one match in each knockout round to confirm grouping.
        Match.objects.create(
            round=self.round_32, stadium=self.stadium,
            home_team=self.tbd_h, away_team=self.tbd_a,
            match_datetime=timezone.now(),
        )
        Match.objects.create(
            round=self.round_16, stadium=self.stadium,
            home_team=self.tbd_h, away_team=self.tbd_a,
            match_datetime=timezone.now() + datetime.timedelta(days=1),
        )
        Match.objects.create(
            round=self.round_8, stadium=self.stadium,
            home_team=self.tbd_h, away_team=self.tbd_a,
            match_datetime=timezone.now() + datetime.timedelta(days=2),
        )
        Match.objects.create(
            round=self.round_semi, stadium=self.stadium,
            home_team=self.tbd_h, away_team=self.tbd_a,
            match_datetime=timezone.now() + datetime.timedelta(days=3),
        )
        Match.objects.create(
            round=self.round_final, stadium=self.stadium,
            home_team=self.tbd_h, away_team=self.tbd_a,
            match_datetime=timezone.now() + datetime.timedelta(days=4),
        )
        response = self.client.get(reverse('match_bracket'))
        self.assertEqual(response.status_code, 200)
        rounds = response.context['rounds']
        self.assertEqual(len(rounds), 5)
        # Ordered by round.order — 16-avos first.
        self.assertEqual(rounds[0]['phase'], 'trinta_dois_avos')
        self.assertEqual(rounds[-1]['phase'], 'final')
        # Third place is exposed as a separate key.
        self.assertIsNone(response.context['third_place_match'])
        # Now add a real 3rd-place match and confirm the slot fills.
        Match.objects.create(
            round=self.round_3rd, stadium=self.stadium,
            home_team=self.team_a, away_team=self.team_b,
            match_datetime=timezone.now() + datetime.timedelta(days=5),
        )
        response2 = self.client.get(reverse('match_bracket'))
        self.assertIsNotNone(response2.context['third_place_match'])


class DateConverterTests(TestCase):
    """Smoke test the custom path converter registration."""

    def test_match_schedule_url_with_date_kwarg_resolves(self):
        # If the converter were not registered, this would 404 with
        # a "no route matches" rather than rendering the view.
        response = self.client.get('/matches/schedule/2026-06-15/')
        # Anonymous user → redirect to login (302), not 404.
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])
