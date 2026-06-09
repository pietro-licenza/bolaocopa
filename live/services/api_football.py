"""
HTTP client for the API-Football v3 service.

Encapsulates the low-level HTTP details (URL composition, authentication
header, error handling and logging) so the rest of the codebase can work
with plain Python dicts / lists. Uses ``urllib.request`` from the standard
library to avoid adding a runtime dependency on the ``requests`` package.
"""

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings


logger = logging.getLogger(__name__)


class ApiFootballClient:
    """Thin wrapper around the API-Football v3 REST endpoints we need."""

    def __init__(
        self,
        api_key=None,
        base_url=None,
        league_id=None,
        season=None,
        timeout=None,
    ):
        self.api_key = api_key or getattr(settings, 'API_FOOTBALL_KEY', '')
        self.base_url = (base_url or getattr(
            settings, 'API_FOOTBALL_BASE_URL',
            'https://v3.football.api-sports.io',
        )).rstrip('/')
        self.league_id = league_id if league_id is not None else getattr(
            settings, 'API_FOOTBALL_LEAGUE_ID', 1,
        )
        self.season = season if season is not None else getattr(
            settings, 'API_FOOTBALL_SEASON', 2026,
        )
        self.timeout = timeout if timeout is not None else getattr(
            settings, 'API_FOOTBALL_TIMEOUT', 15,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_fixture(self, fixture_id):
        """Return the raw fixture dict, or ``None`` on any error."""
        payload = self._get('/fixtures', {'id': fixture_id})
        if not payload:
            return None
        response = payload.get('response') or []
        if not response:
            return None
        return response[0]

    def get_fixtures_by_date(self, date_str):
        """Return a list of fixture dicts for ``date_str`` (YYYY-MM-DD)."""
        payload = self._get('/fixtures', {
            'date': date_str,
            'league': self.league_id,
            'season': self.season,
        })
        if not payload:
            return []
        return payload.get('response') or []

    def get_fixture_events(self, fixture_id):
        """Return the list of events for a given fixture, or ``[]``."""
        payload = self._get('/fixtures/events', {'fixture': fixture_id})
        if not payload:
            return []
        return payload.get('response') or []

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get(self, path, params):
        """Perform a GET request and return the parsed JSON payload.

        Returns ``None`` when the request fails for any reason
        (network error, non-2xx status, malformed body). All errors are
        logged with enough context to debug.
        """
        if not self.api_key:
            logger.error(
                '[API-Football] Missing API key (set API_FOOTBALL_KEY).',
            )
            return None

        url = '{base}{path}?{query}'.format(
            base=self.base_url,
            path=path,
            query=urllib.parse.urlencode(params),
        )
        request = urllib.request.Request(url, method='GET')
        request.add_header('x-apisports-key', self.api_key)
        request.add_header('Accept', 'application/json')

        # Build an SSL context that uses certifi's CA bundle when available
        # (workaround for Python 3.14 on macOS where the system cert store
        # is not wired up automatically). Falls back to the default context
        # if certifi is not installed.
        ssl_context = None
        if self.base_url.startswith('https://'):
            try:
                import certifi
                import ssl
                ssl_context = ssl.create_default_context(
                    cafile=certifi.where(),
                )
            except ImportError:
                ssl_context = None

        start = time.monotonic()
        status = 'ERR'
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout, context=ssl_context,
            ) as resp:
                status = str(resp.status)
                body = resp.read()
        except urllib.error.HTTPError as exc:
            status = str(exc.code)
            logger.exception(
                '[API-Football] HTTP %s on GET %s',
                exc.code, path,
            )
            self._log_call(path, params, status, start)
            return None
        except urllib.error.URLError as exc:
            logger.exception(
                '[API-Football] URLError on GET %s: %s', path, exc.reason,
            )
            self._log_call(path, params, status, start)
            return None
        except (TimeoutError, OSError) as exc:
            # OSError also covers ssl.SSLCertVerificationError and
            # any other low-level socket/SSL failures.
            logger.exception(
                '[API-Football] Timeout/connection error on GET %s: %s',
                path, exc,
            )
            self._log_call(path, params, status, start)
            return None

        self._log_call(path, params, status, start)

        try:
            return json.loads(body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            logger.exception(
                '[API-Football] Failed to decode JSON response from GET %s',
                path,
            )
            return None

    def _log_call(self, path, params, status, start):
        elapsed_ms = int((time.monotonic() - start) * 1000)
        query = urllib.parse.urlencode(params)
        logger.info(
            '[API-Football] GET %s?%s — %s — %dms',
            path, query, status, elapsed_ms,
        )
