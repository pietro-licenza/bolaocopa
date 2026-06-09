"""
HTTP client for the football-data.org v4 service.

Encapsulates the low-level HTTP details (URL composition, authentication
header, error handling and logging) so the rest of the codebase can work
with plain Python dicts / lists. Uses ``urllib.request`` from the standard
library to avoid adding a runtime dependency on the ``requests`` package.

The football-data.org free tier covers the FIFA World Cup officially,
which is the reason this client is the primary source for backfilling
``Match.external_id`` and for the live score / status sync. Detailed
event data (goals / cards / subs) is limited on the free tier, so for
that kind of data the API-Football client is preferred (see
``live/services/router.py``).
"""

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings


logger = logging.getLogger(__name__)


class FootballDataOrgClient:
    """Thin wrapper around the football-data.org v4 REST endpoints we need."""

    def __init__(
        self,
        api_key=None,
        base_url=None,
        world_cup_id=None,
        timeout=None,
    ):
        self.api_key = api_key or getattr(
            settings, 'FOOTBALL_DATA_ORG_KEY', '',
        )
        self.base_url = (base_url or getattr(
            settings, 'FOOTBALL_DATA_ORG_BASE_URL',
            'https://api.football-data.org/v4',
        )).rstrip('/')
        self.world_cup_id = world_cup_id if world_cup_id is not None else getattr(
            settings, 'FOOTBALL_DATA_ORG_WORLD_CUP_ID', 2000,
        )
        self.timeout = timeout if timeout is not None else getattr(
            settings, 'FOOTBALL_DATA_ORG_TIMEOUT', 15,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_match(self, match_id):
        """Return the raw match dict, or ``None`` on any error.

        Endpoint: ``GET /matches/{match_id}``.
        """
        payload = self._get('/matches/{0}'.format(match_id))
        if not payload:
            return None
        # The endpoint returns the match object directly (no wrapping
        # ``response`` array like API-Football does).
        return payload

    def get_competition_matches(self, competition_id, date_from=None, date_to=None):
        """Return a list of match dicts for a competition.

        Endpoint: ``GET /competitions/{id}/matches?dateFrom=&dateTo=``.

        ``date_from`` and ``date_to`` must be ``YYYY-MM-DD`` strings when
        provided. Returns an empty list on error.
        """
        params = {}
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        payload = self._get(
            '/competitions/{0}/matches'.format(competition_id), params,
        )
        if not payload:
            return []
        return payload.get('matches') or []

    def get_standings(self, competition_id):
        """Return a list of standing groups for a competition.

        Endpoint: ``GET /competitions/{id}/standings``.

        Each item in the returned list represents a group (the 2026 World
        Cup has 12 groups, A through L). Returns an empty list on error.
        """
        payload = self._get(
            '/competitions/{0}/standings'.format(competition_id),
        )
        if not payload:
            return []
        standings = payload.get('standings') or []
        return standings

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get(self, path, params=None):
        """Perform a GET request and return the parsed JSON payload.

        Returns ``None`` when the request fails for any reason (network
        error, non-2xx status, malformed body, missing API key). All
        errors are logged with enough context to debug.
        """
        if not self.api_key:
            logger.error(
                '[FDO] Missing API key (set FOOTBALL_DATA_ORG_KEY).',
            )
            return None

        params = params or {}
        url = '{base}{path}'.format(base=self.base_url, path=path)
        if params:
            url = '{0}?{1}'.format(url, urllib.parse.urlencode(params))
        request = urllib.request.Request(url, method='GET')
        request.add_header('X-Auth-Token', self.api_key)
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
                '[FDO] HTTP %s on GET %s', exc.code, path,
            )
            self._log_call(path, params, status, start)
            return None
        except urllib.error.URLError as exc:
            logger.exception(
                '[FDO] URLError on GET %s: %s', path, exc.reason,
            )
            self._log_call(path, params, status, start)
            return None
        except (TimeoutError, OSError) as exc:
            # OSError also covers ssl.SSLCertVerificationError and
            # any other low-level socket/SSL failures.
            logger.exception(
                '[FDO] Timeout/connection error on GET %s: %s', path, exc,
            )
            self._log_call(path, params, status, start)
            return None

        self._log_call(path, params, status, start)

        try:
            return json.loads(body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            logger.exception(
                '[FDO] Failed to decode JSON response from GET %s', path,
            )
            return None

    def _log_call(self, path, params, status, start):
        elapsed_ms = int((time.monotonic() - start) * 1000)
        query = urllib.parse.urlencode(params) if params else ''
        logger.info(
            '[FDO] GET %s%s — %s — %dms',
            path, ('?' + query) if query else '', status, elapsed_ms,
        )
