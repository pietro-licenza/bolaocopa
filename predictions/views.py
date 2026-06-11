from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView

from matches.models import Match
from pools.models import Pool, PoolMember

from .forms import PredictionForm
from .models import Prediction


class PoolMatchListView(LoginRequiredMixin, ListView):
    template_name = 'predictions/pool_matches.html'
    context_object_name = 'matches'

    def get_queryset(self):
        self.pool = get_object_or_404(Pool, pk=self.kwargs['pool_id'])
        return Match.objects.select_related(
            'home_team', 'away_team', 'stadium', 'round',
        ).order_by('match_datetime')

    def dispatch(self, request, *args, **kwargs):
        self.pool = get_object_or_404(Pool, pk=self.kwargs['pool_id'])
        if not PoolMember.objects.filter(
            pool=self.pool,
            user=request.user,
        ).exists():
            messages.error(request, 'Você precisa ser membro deste bolão para acessar.')
            return redirect(reverse('pool_detail', kwargs={'pk': self.pool.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.pool
        now = timezone.now()
        user_predictions = {
            p.match_id: p for p in Prediction.objects.filter(
                user=self.request.user,
                pool=self.pool,
            )
        }
        match_items = []
        for match in context['matches']:
            is_locked = match.match_datetime <= now
            prediction = user_predictions.get(match.pk)
            match_items.append({
                'match': match,
                'is_locked': is_locked,
                'user_prediction': prediction,
                'points_earned': prediction.points if prediction and match.status == 'finalizado' else None,
                'show_points': prediction is not None and match.status == 'finalizado',
            })
        context['match_items'] = match_items
        return context


class PredictionCreateView(LoginRequiredMixin, CreateView):
    model = Prediction
    form_class = PredictionForm
    template_name = 'predictions/prediction_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.pool = get_object_or_404(Pool, pk=kwargs['pool_id'])
        self.match = get_object_or_404(Match, pk=kwargs['match_id'])
        if not PoolMember.objects.filter(
            pool=self.pool,
            user=request.user,
        ).exists():
            messages.error(request, 'Você precisa ser membro deste bolão.')
            return redirect(reverse('pool_detail', kwargs={'pk': self.pool.pk}))
        if self.match.match_datetime <= timezone.now():
            messages.error(request, 'Palpite indisponível - jogo já começou.')
            return redirect(reverse(
                'pool_matches',
                kwargs={'pool_id': self.pool.pk},
            ))
        if Prediction.objects.filter(
            user=request.user,
            match=self.match,
            pool=self.pool,
        ).exists():
            messages.info(request, 'Você já palpitou neste jogo. Edite seu palpite se necessário.')
            return redirect(reverse(
                'pool_matches',
                kwargs={'pool_id': self.pool.pk},
            ))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['match'] = self.match
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.pool
        context['match'] = self.match
        context['is_locked'] = False
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.match = self.match
        form.instance.pool = self.pool
        messages.success(self.request, 'Palpite registrado com sucesso!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pool_matches', kwargs={'pool_id': self.pool.pk})


class PredictionUpdateView(LoginRequiredMixin, UpdateView):
    model = Prediction
    form_class = PredictionForm
    template_name = 'predictions/prediction_form.html'
    context_object_name = 'prediction'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Prediction,
            user=self.request.user,
            match=self.match,
            pool=self.pool,
        )

    def dispatch(self, request, *args, **kwargs):
        self.pool = get_object_or_404(Pool, pk=kwargs['pool_id'])
        self.match = get_object_or_404(Match, pk=kwargs['match_id'])
        if self.match.match_datetime <= timezone.now():
            messages.error(request, 'Palpite indisponível - jogo já começou.')
            return redirect(reverse(
                'pool_matches',
                kwargs={'pool_id': self.pool.pk},
            ))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['match'] = self.match
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.pool
        context['match'] = self.match
        context['is_locked'] = False
        context['is_editing'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Palpite atualizado com sucesso!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('pool_matches', kwargs={'pool_id': self.pool.pk})


class MyPredictionsListView(LoginRequiredMixin, ListView):
    template_name = 'predictions/my_predictions.html'
    context_object_name = 'prediction_items'

    def get_queryset(self):
        self.pool = get_object_or_404(Pool, pk=self.kwargs['pool_id'])
        return Prediction.objects.filter(
            user=self.request.user,
            pool=self.pool,
        ).select_related(
            'match__home_team',
            'match__away_team',
            'match__stadium',
            'match__round',
        ).order_by('match__match_datetime')

    def dispatch(self, request, *args, **kwargs):
        self.pool = get_object_or_404(Pool, pk=self.kwargs['pool_id'])
        if not PoolMember.objects.filter(
            pool=self.pool,
            user=request.user,
        ).exists():
            messages.error(request, 'Você precisa ser membro deste bolão para acessar.')
            return redirect(reverse('pool_detail', kwargs={'pk': self.pool.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.pool
        now = timezone.now()
        items = []
        total_points = 0
        for prediction in context['prediction_items']:
            match = prediction.match
            if match.status == 'finalizado':
                status_label = 'finalizado'
            elif match.match_datetime <= now:
                status_label = 'bloqueado'
            else:
                status_label = 'editavel'
            total_points += prediction.points or 0
            items.append({
                'prediction': prediction,
                'match': match,
                'home_team': match.home_team,
                'away_team': match.away_team,
                'match_datetime': match.match_datetime,
                'stadium': match.stadium,
                'round': match.round,
                'predicted_home_score': prediction.home_score,
                'predicted_away_score': prediction.away_score,
                'points_earned': prediction.points or 0,
                'status_label': status_label,
            })
        context['prediction_items'] = items
        context['totals'] = {
            'total_predictions': len(items),
            'total_points': total_points,
        }
        return context
