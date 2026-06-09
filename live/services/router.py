"""
Hybrid router that decides which external API to call based on the kind
of data being requested.

Strategy (per Epic 7 of ``TASKS.md``):

* **Backfill of external IDs / discovery of matches**:
  football-data.org (official, always available, covers FIFA World Cup
  on the free tier). API-Football is a fallback when FDO returns nothing.
* **Live score / status / standings**:
  football-data.org first, API-Football as a fallback.
* **Detailed events (goals / cards / subs)**:
  API-Football first (richer data on the free tier), FDO as a basic
  fallback (which often returns no events on the free plan).

A small in-memory cache is kept on the router instance so that, within
the lifetime of a single request (a management command run or a Django
view), we never make the same upstream call twice.
"""

import logging

from live.services.api_football import ApiFootballClient
from live.services.football_data_org import FootballDataOrgClient


logger = logging.getLogger(__name__)


class LiveDataRouter:
    """Pick the right API client for each kind of query."""

    def __init__(
        self,
        fdo_client=None,
        api_football_client=None,
        world_cup_id=None,
    ):
        # ``None`` lets the client fall back to its own settings defaults.
        self.fdo = fdo_client if fdo_client is not None else FootballDataOrgClient()
        self.api_football = (
            api_football_client if api_football_client is not None
            else ApiFootballClient()
        )
        self.world_cup_id = (
            world_cup_id if world_cup_id is not None
            else self.fdo.world_cup_id
        )
        # Simple per-instance in-memory cache, keyed by the underlying
        # method arguments. This is intentionally process-local: the
        # expectation is that one command run / one view call may end
        # up asking the same question multiple times, and we should not
        # burn quota for that.
        self._cache = {}

    # ------------------------------------------------------------------
    # Match discovery (backfill)
    # ------------------------------------------------------------------

    def find_world_cup_match(self, date_from, date_to):
        """Return all WC matches in ``[date_from, date_to]``.

        Tries football-data.org first (the official source). On empty
        result or error, falls back to API-Football (one call per day
        inside the range). The result is cached for repeat calls with
        the same arguments within this router's lifetime.
        """
        cache_key = ('find_world_cup_match', date_from, date_to)
        if cache_key in self._cache:
            return self._cache[cache_key]

        fdo_matches = self.fdo.get_competition_matches(
            self.world_cup_id, date_from=date_from, date_to=date_to,
        )
        if fdo_matches:
            logger.info(
                '[Router] FDO returned %d match(es) for %s..%s.',
                len(fdo_matches), date_from, date_to,
            )
            self._cache[cache_key] = fdo_matches
            return fdo_matches

        logger.info(
            '[Router] FDO returned no matches for %s..%s; '
            'falling back to API-Football per-day.',
            date_from, date_to,
        )
        af_matches = []
        # Walk the date range one day at a time. The number of days is
        # bounded (e.g. ~39 for the 2026 World Cup), and we early-exit
        # as soon as the FDO response is non-empty.
        from datetime import date as date_type
        from datetime import timedelta
        try:
            start = date_type.fromisoformat(date_from)
            end = date_type.fromisoformat(date_to)
        except ValueError:
            logger.exception(
                '[Router] Invalid date format passed to '
                'find_world_cup_match: %r / %r',
                date_from, date_to,
            )
            self._cache[cache_key] = []
            return []

        cursor = start
        while cursor <= end:
            day_str = cursor.strftime('%Y-%m-%d')
            day_matches = self.api_football.get_fixtures_by_date(day_str)
            if day_matches:
                af_matches.extend(day_matches)
            cursor += timedelta(days=1)

        logger.info(
            '[Router] API-Football fallback returned %d match(es) for %s..%s.',
            len(af_matches), date_from, date_to,
        )
        self._cache[cache_key] = af_matches
        return af_matches

    # ------------------------------------------------------------------
    # Live score / status
    # ------------------------------------------------------------------

    def get_match_live_data(self, match):
        """Return the freshest match payload we can find for ``match``.

        ``match`` is a ``matches.models.Match`` instance. The router
        uses ``match.external_id`` (if present) to look up the game
        directly on football-data.org first, then API-Football.
        """
        external_id = getattr(match, 'external_id', None)
        if external_id is None:
            logger.info(
                '[Router] Match %s has no external_id; cannot look up '
                'live data.',
                match.pk,
            )
            return None

        cache_key = ('get_match_live_data', external_id)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # football-data.org first: official source, usually populated.
        fdo_match = self.fdo.get_match(external_id)
        if fdo_match:
            self._cache[cache_key] = fdo_match
            return fdo_match

        # Fallback to API-Football.
        af_match = self.api_football.get_fixture(external_id)
        self._cache[cache_key] = af_match
        return af_match

    # ------------------------------------------------------------------
    # Detailed events
    # ------------------------------------------------------------------

    def get_match_events(self, match):
        """Return a list of event dicts for ``match``.

        API-Football is the primary source because its free tier exposes
        rich event data (goals / cards / substitutions). football-data.org
        is a basic fallback that often returns no events on the free plan.
        """
        external_id = getattr(match, 'external_id', None)
        if external_id is None:
            return []

        cache_key = ('get_match_events', external_id)
        if cache_key in self._cache:
            return self._cache[cache_key]

        af_events = self.api_football.get_fixture_events(external_id)
        if af_events:
            self._cache[cache_key] = af_events
            return af_events

        # football-data.org does not expose /matches/{id}/events as a
        # first-class endpoint; the events live embedded in the match
        # payload under ``goals`` / ``bookings``. We return an empty list
        # rather than guess at the shape, leaving room for a future
        # implementation to extract those embedded fields.
        fdo_match = self.fdo.get_match(external_id)
        if fdo_match:
            logger.info(
                '[Router] API-Football returned no events for match %s; '
                'football-data.org fallback left as future work.',
                external_id,
            )
        self._cache[cache_key] = []
        return []

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def clear_cache(self):
        """Reset the in-memory cache (mainly for tests)."""
        self._cache = {}
