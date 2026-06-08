from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import PoolForm
from .models import Pool, PoolMember


class PoolCreateView(LoginRequiredMixin, CreateView):
    model = Pool
    form_class = PoolForm
    template_name = 'pools/pool_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        PoolMember.objects.create(pool=self.object, user=self.request.user)
        return response

    def get_success_url(self):
        return reverse('pool_detail', kwargs={'pk': self.object.pk})


class PoolDetailView(LoginRequiredMixin, DetailView):
    model = Pool
    template_name = 'pools/pool_detail.html'
    context_object_name = 'pool'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member'] = PoolMember.objects.filter(
            pool=self.object,
            user=self.request.user,
        ).exists()
        members_qs = self.object.members.select_related('user').order_by(
            'joined_at',
        )
        ranked_members = []
        for index, member in enumerate(members_qs, start=1):
            ranked_members.append({
                'position': index,
                'name': member.user.get_full_name() or member.user.email,
                'email': member.user.email,
                'is_creator': member.user == self.object.created_by,
                'points': 0,
            })
        ranked_members.sort(key=lambda m: (-m['points'], m['position']))
        for index, member in enumerate(ranked_members, start=1):
            member['position'] = index
        context['ranked_members'] = ranked_members
        context['member_count'] = len(ranked_members)
        return context


class PoolJoinView(LoginRequiredMixin, DetailView):
    model = Pool
    template_name = 'pools/pool_join.html'
    context_object_name = 'pool'
    slug_field = 'invite_token'
    slug_url_kwarg = 'token'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except (Pool.DoesNotExist, Http404):
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            messages.error(request, 'Link de convite inválido ou expirado.')
            return redirect(reverse('pool_list'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member'] = PoolMember.objects.filter(
            pool=self.object,
            user=self.request.user,
        ).exists()
        context['member_count'] = self.object.members.count()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            messages.error(request, 'Link de convite inválido ou expirado.')
            return redirect(reverse('pool_list'))
        if PoolMember.objects.filter(pool=self.object, user=request.user).exists():
            return redirect(reverse('pool_detail', kwargs={'pk': self.object.pk}))
        PoolMember.objects.create(pool=self.object, user=request.user)
        messages.success(request, 'Você entrou no bolão com sucesso!')
        return redirect(reverse('pool_detail', kwargs={'pk': self.object.pk}))


class PoolListView(LoginRequiredMixin, ListView):
    model = Pool
    template_name = 'pools/pool_list.html'
    context_object_name = 'pools'

    def get_queryset(self):
        return Pool.objects.filter(members__user=self.request.user)