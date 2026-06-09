from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from pools.models import Pool, PoolMember


class PoolRankingListView(LoginRequiredMixin, ListView):
    template_name = 'rankings/pool_ranking.html'
    context_object_name = 'ranking_items'

    def dispatch(self, request, *args, **kwargs):
        self.pool = get_object_or_404(Pool, pk=kwargs['pool_id'])
        if not PoolMember.objects.filter(
            pool=self.pool,
            user=request.user,
        ).exists():
            messages.error(request, 'Voce precisa ser membro deste bolao.')
            return redirect(reverse('pool_detail', kwargs={'pk': self.pool.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        members = PoolMember.objects.filter(
            pool=self.pool,
        ).select_related('user').annotate(
            total_points=Sum(
                'user__predictions__points',
                filter=Q(user__predictions__pool=self.pool),
            ),
            predictions_count=Count(
                'user__predictions',
                filter=Q(user__predictions__pool=self.pool),
            ),
        ).order_by('-total_points', 'joined_at')
        return members

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = []
        for index, m in enumerate(context['ranking_items'], start=1):
            items.append({
                'position': index,
                'name': m.user.get_full_name() or m.user.email,
                'email': m.user.email,
                'is_creator': m.user == self.pool.created_by,
                'is_current_user': m.user == self.request.user,
                'total_points': m.total_points or 0,
                'predictions_count': m.predictions_count or 0,
            })
        context['ranking_items'] = items
        context['pool'] = self.pool
        return context
