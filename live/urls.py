from django.urls import path

from .views import MatchSyncView


urlpatterns = [
    path(
        'matches/<int:match_id>/sync/',
        MatchSyncView.as_view(),
        name='match_sync',
    ),
]
