"""
Smoke tests for the API-Football client.

The HTTP layer is patched so the test does not hit the real API
(and does not consume the 100 req/day free-tier quota).
"""

import io
import json
import unittest
from unittest import mock

from django.test import SimpleTestCase, override_settings

from live.services.api_football import ApiFootballClient


FIXTURE_URL = 'https://v3.football.api-sports.io/fixtures'
EVENTS_URL = 'https://v3.football.api-sports.io/fixtures/events'
API_KEY = 'd44477e3b2d6ab2ddae8b6d5fa7207c6'


def _make_response(body, status=200):
    """Build a minimal file-like object with the ``status`` attribute."""
    raw = json.dumps(body).encode('utf-8') if not isinstance(
        body, bytes,
    ) else body
    response = io.BytesIO(raw)
    response.status = status
    return response


@override_settings(
    API_FOOTBALL_KEY=API_KEY,
    API_FOOTBALL_BASE_URL='https://v3.football.api-sports.io',
    API_FOOTBALL_LEAGUE_ID=1,
    API_FOOTBALL_SEASON=2026,
)
class ApiFootballClientTests(SimpleTestCase):
    """Verify URL composition, headers and basic payload parsing."""

    def _assert_request(self, request, expected_url, expected_header):
        self.assertEqual(request.full_url, expected_url)
        # urllib stores headers verbatim (case-sensitive). Look up the
        # auth header by its exact key in header_items() instead of
        # relying on request.get_header(), which is unreliable for
        # non-standard header names.
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
            '{0}?id=123'.format(FIXTURE_URL),
            API_KEY,
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
            '{0}?date=2026-06-11&league=1&season=2026'.format(FIXTURE_URL),
            API_KEY,
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
            '{0}?fixture=456'.format(EVENTS_URL),
            API_KEY,
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


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
