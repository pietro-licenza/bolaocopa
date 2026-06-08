from django.urls import path

from .views import (
    MyPredictionsListView,
    PoolMatchListView,
    PredictionCreateView,
    PredictionUpdateView,
)

urlpatterns = [
    path(
        'pools/<int:pool_id>/matches/',
        PoolMatchListView.as_view(),
        name='pool_matches',
    ),
    path(
        'pools/<int:pool_id>/predictions/',
        MyPredictionsListView.as_view(),
        name='my_predictions',
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
