"""
Static mapping of FIFA World Cup 2026 groups (A through L).

The ``Team`` model does not carry a ``group`` field — that association
is *not* normalised in the schema on purpose: a team belongs to a
group only for the duration of a single World Cup, and the per-tournament
draw can change between editions. Storing it on the team would force
historical gymnastics whenever a future draw happens.

Instead, this module exposes the official draw composition as a plain
Python dict, keyed by group letter, with lists of 3-letter FIFA country
codes (matching ``Team.country_code``). The draw is the single source
of truth for "which team is in which group"; views and tests consult
this mapping whenever they need to bucket teams.

Source of truth
---------------
The 2026 World Cup draw took place on **December 5, 2025** at the
Kennedy Center in Washington, D.C. (see the Wikipedia article
"2026 FIFA World Cup draw" and FIFA's "Draw Procedures for the FIFA
World Cup 2026" PDF). The composition below mirrors the official
groups published after the ceremony. The 4 UEFA playoff placeholders
that were drawn into the groups (later resolved on March 31, 2026)
have been replaced with the actual winners:

* **B2** = Bosnia and Herzegovina  (UEFA Path A winner)
* **D4** = Turkey                  (UEFA Path C winner)
* **F3** = Sweden                  (UEFA Path B winner)
* **A4** = Czech Republic / Czechia (UEFA Path D winner)

* **E3** = IC Path 1 winner (Congo DR, filled from the inter-confederation
  playoff).

The IC Path 2 placeholder (note D in the Wikipedia article) was the
only placeholder that ended up in a different position from its draw
slot. The final composition below is the one used by FIFA for the
match schedule published after the playoffs.
"""

WORLD_CUP_2026_GROUPS = {
    'A': ['MEX', 'RSA', 'KOR', 'CZE'],
    'B': ['CAN', 'BIH', 'QAT', 'SUI'],
    'C': ['BRA', 'MAR', 'HAI', 'SCO'],
    'D': ['USA', 'PAR', 'AUS', 'TUR'],
    'E': ['GER', 'CUW', 'CIV', 'ECU'],
    'F': ['NED', 'JPN', 'SWE', 'TUN'],
    'G': ['BEL', 'EGY', 'IRN', 'NZL'],
    'H': ['ESP', 'CPV', 'KSA', 'URU'],
    'I': ['FRA', 'SEN', 'IRQ', 'NOR'],
    'J': ['ARG', 'ALG', 'AUT', 'JOR'],
    'K': ['POR', 'COD', 'UZB', 'COL'],
    'L': ['ENG', 'CRO', 'GHA', 'PAN'],
}

# Inverse index: country_code -> group letter. Built once at import
# time so ``get_group_for_team`` is O(1) and we don't re-scan the dict
# for every match in the queryset.
_TEAM_TO_GROUP = {}
for _group_letter, _codes in WORLD_CUP_2026_GROUPS.items():
    for _code in _codes:
        _TEAM_TO_GROUP[_code] = _group_letter


def get_group_for_team(country_code):
    """Return the group letter (``'A'``..``'L'``) for ``country_code``.

    Returns ``None`` when the code is not part of the 2026 draw — for
    example, the ``TBD-H`` / ``TBD-A`` placeholders used in the
    knockout stage while group winners are still unknown, or codes
    that do not exist in the database.
    """
    if not country_code:
        return None
    return _TEAM_TO_GROUP.get(country_code)


def get_all_groups():
    """Return the list of group letters in alphabetical order."""
    return sorted(WORLD_CUP_2026_GROUPS.keys())
