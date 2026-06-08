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
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from pools.models import Pool, PoolMember

from .forms import (
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomUserCreationForm,
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
        return context


class LandingView(TemplateView):
    template_name = 'pages/landing.html'