from django.urls import path

from .views import (
    PoolCreateView,
    PoolDetailView,
    PoolJoinView,
    PoolLeaveView,
    PoolListView,
    RulesView,
)

urlpatterns = [
    path('pools/', PoolListView.as_view(), name='pool_list'),
    path('pools/create/', PoolCreateView.as_view(), name='pool_create'),
    path('pools/join/<uuid:token>/', PoolJoinView.as_view(), name='pool_join'),
    path('pools/<int:pk>/', PoolDetailView.as_view(), name='pool_detail'),
    path('pools/<int:pk>/leave/', PoolLeaveView.as_view(), name='pool_leave'),
    path('pools/rules/', RulesView.as_view(), name='pool_rules'),
]