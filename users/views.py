from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, TemplateView, UpdateView

from matches.models import Match
from pools.models import Pool, PoolMember
from predictions.models import Prediction
from rankings.models import Ranking

from .forms import (
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomUserCreationForm,
    UserProfileForm,
)
from .models import CustomUser


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = CustomAuthenticationForm


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    form_class = CustomSetPasswordForm


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # User pools with position info
        user_pools = Pool.objects.filter(members__user=self.request.user)
        pools_with_position = []
        for pool in user_pools:
            member_count = PoolMember.objects.filter(pool=pool).count()
            user_member = PoolMember.objects.get(pool=pool, user=self.request.user)
            position = PoolMember.objects.filter(
                pool=pool,
                joined_at__lt=user_member.joined_at,
            ).count() + 1
            pools_with_position.append({
                'pool': pool,
                'member_count': member_count,
                'position': position,
            })
        context['user_pools'] = pools_with_position
        context['pool_count'] = user_pools.count()

        # Check if user is member of any pool
        is_pool_member = user_pools.exists()
        context['is_pool_member'] = is_pool_member

        # Total predictions count
        total_predictions = Prediction.objects.filter(user=self.request.user).count()
        context['prediction_count'] = total_predictions

        # Total points across all pools
        total_points = Ranking.objects.filter(user=self.request.user).aggregate(
            total=models.Sum('total_points')
        )['total'] or 0
        context['total_points'] = total_points

        # Recent predictions: next 5 matches with user predictions (match_datetime > now)
        # Filter: user predictions for matches that haven't started yet
        recent_predictions = Prediction.objects.filter(
            user=self.request.user,
            match__match_datetime__gt=now,
            match__status='agendado',
        ).select_related(
            'match__home_team',
            'match__away_team',
            'pool',
        ).order_by('match__match_datetime')[:5]

        prediction_items = []
        for pred in recent_predictions:
            match = pred.match
            status_label = 'editavel'
            prediction_items.append({
                'prediction': pred,
                'match': match,
                'home_team': match.home_team,
                'away_team': match.away_team,
                'home_score': pred.home_score,
                'away_score': pred.away_score,
                'pool_name': pred.pool.name,
                'status_label': status_label,
            })
        context['recent_predictions'] = prediction_items

        # Next matches available for prediction (next 5, not started yet)
        upcoming_matches = Match.objects.filter(
            match_datetime__gt=now,
            status='agendado',
        ).select_related(
            'home_team',
            'away_team',
            'stadium',
            'round',
        ).order_by('match_datetime')[:5]

        match_items = []
        for match in upcoming_matches:
            match_items.append({
                'match': match,
                'home_team': match.home_team,
                'away_team': match.away_team,
                'match_datetime': match.match_datetime,
            })
        context['upcoming_matches'] = match_items

        return context


class LandingView(TemplateView):
    template_name = 'pages/landing.html'


class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        from django.contrib import messages
        messages.success(self.request, 'Perfil atualizado')
        return response