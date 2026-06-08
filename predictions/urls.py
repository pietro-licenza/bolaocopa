from django.urls import path

from .views import PoolMatchListView, PredictionCreateView, PredictionUpdateView

urlpatterns = [
    path(
        'pools/<int:pool_id>/matches/',
        PoolMatchListView.as_view(),
        name='pool_matches',
    ),
    path(
        'pools/<int:pool_id>/matches/<int:match_id>/predict/',
        PredictionCreateView.as_view(),
        name='prediction_create',
    ),
    path(
        'pools/<int:pool_id>/matches/<int:match_id>/edit/',
        PredictionUpdateView.as_view(),
        name='prediction_update',
    ),
]
