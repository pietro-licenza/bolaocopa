from django.contrib.auth.mixins import LoginRequiredMixin
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
        return context


class PoolListView(LoginRequiredMixin, ListView):
    model = Pool
    template_name = 'pools/pool_list.html'
    context_object_name = 'pools'

    def get_queryset(self):
        return Pool.objects.filter(members__user=self.request.user)