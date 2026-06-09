from django.urls import path

from .views import MatchCardPartialView, MatchSyncView


urlpatterns = [
    # Polling endpoint used by US-7.4: returns the rendered HTML of a
    # single match card so the frontend can refresh the scoreboard
    # every 60s for games in progress, without reloading the whole
    # page. Logged-in only.
    path(
        'matches/<int:match_id>/_partial/',
        MatchCardPartialView.as_view(),
        name='match_card_partial',
    ),
    path(
        'matches/<int:match_id>/sync/',
        MatchSyncView.as_view(),
        name='match_sync',
    ),
]
