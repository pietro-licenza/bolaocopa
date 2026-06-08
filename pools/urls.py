from django.urls import path

from .views import PoolCreateView, PoolDetailView, PoolListView

urlpatterns = [
    path('pools/', PoolListView.as_view(), name='pool_list'),
    path('pools/create/', PoolCreateView.as_view(), name='pool_create'),
    path('pools/<int:pk>/', PoolDetailView.as_view(), name='pool_detail'),
]