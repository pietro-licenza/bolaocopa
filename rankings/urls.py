from django.urls import path

from .views import PoolRankingListView

urlpatterns = [
    path(
        'pools/<int:pool_id>/ranking/',
        PoolRankingListView.as_view(),
        name='pool_ranking',
    ),
]
