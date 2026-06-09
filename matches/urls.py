from django.urls import path

from .views import (
    MatchBracketView,
    MatchGroupsView,
    MatchHomeView,
    MatchListView,
    MatchScheduleView,
)


urlpatterns = [
    # US-7.7: dedicated "Jogos" landing page. The three sub-views
    # (Agenda / Grupos / Chaveamento) are reachable from here and
    # also from the navbar. Mounted at the empty path so the
    # include() in ``core.urls`` (``path('matches/', include(...))``)
    # produces the canonical ``/matches/`` URL.
    path('', MatchHomeView.as_view(), name='match_home'),
    # ``<date:date>`` is registered in ``core.urls`` via the
    # ``DateConverter`` class. The pattern with and without the
    # date segment resolve to the same name so reverse() and
    # ``{% url 'match_schedule' %}`` keep working when no date is
    # supplied — the view falls back to "today" in that case.
    path('schedule/', MatchScheduleView.as_view(), name='match_schedule'),
    path(
        'schedule/<date:date>/',
        MatchScheduleView.as_view(),
        name='match_schedule',
    ),
    path('groups/', MatchGroupsView.as_view(), name='match_groups'),
    path('bracket/', MatchBracketView.as_view(), name='match_bracket'),
    # Legacy list view (US-4.1): the original "all matches" page
    # moved under ``/matches/all/`` so it does not collide with the
    # new landing page. The ``match_list`` name is preserved for
    # backwards compatibility with ``live.views.MatchSyncView``'s
    # redirect fallback and the dashboard / navbar links that
    # already point at it.
    path('all/', MatchListView.as_view(), name='match_list'),
]
