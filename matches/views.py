from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from predictions.models import Prediction

from .models import Match


class MatchListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'
    paginate_by = 20

    def get_queryset(self):
        return Match.objects.select_related(
            'home_team', 'away_team', 'stadium', 'round',
        ).order_by('match_datetime')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pool_match_ids = set(
            Prediction.objects.filter(
                user=self.request.user,
            ).values_list('match_id', flat=True)
        )
        match_items = []
        for match in context['matches']:
            match_items.append({
                'match': match,
                'home_team': match.home_team,
                'away_team': match.away_team,
                'match_datetime': match.match_datetime,
                'stadium': match.stadium,
                'round': match.round,
                'status': match.status,
                'user_has_predicted': match.pk in user_pool_match_ids,
            })
        context['match_items'] = match_items
        context['upcoming_count'] = Match.objects.filter(
            status='agendado',
        ).count()
        context['finished_count'] = Match.objects.filter(
            status='finalizado',
        ).count()
        return context
