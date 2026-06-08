# Code Style

## Regras gerais

- **Codigo em ingles.** Identificadores, variaveis, funcoes, classes e comentarios em ingles.
- **Interface em portugues brasileiro.** Todo texto visivel ao usuario em pt-BR, no template, nao na view.
- **PEP08 rigorosamente.** Seguir o guia de estilo do Python sem excecoes.
- **Aspas simples.** Usar aspas simples (`'`) em todas as strings Python e atributos HTML. Aspas duplas (`"`) somente quando a sintaxe exigir.

## Python

### Aspas simples

```python
# Certo
name = models.CharField(max_length=100)
queryset = Prediction.objects.filter(pool=pool)

# Errado
name = models.CharField(max_length=100)
queryset = Prediction.objects.filter(pool=pool)
```

### Class Based Views

```python
# Certo
class PoolListView(LoginRequiredMixin, ListView):
    model = Pool
    context_object_name = 'pools'

    def get_queryset(self):
        return Pool.objects.filter(
            members__user=self.request.user
        )

# Errado - nunca function-based view
def pool_list(request):
    pools = Pool.objects.filter(members__user=request.user)
    return render(request, 'pools/pool_list.html', {'pools': pools})
```

### LoginRequiredMixin

Toda view autenticada herda `LoginRequiredMixin` como primeira mixin:

```python
class PoolCreateView(LoginRequiredMixin, CreateView):
    model = Pool
    form_class = PoolForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
```

### get_queryset filtrado

Views que listam dados do usuario filtram por `self.request.user`:

```python
def get_queryset(self):
    return Prediction.objects.filter(user=self.request.user)
```

### Models: campos audit

Todo modelo tem `created_at` e `updated_at`:

```python
class Pool(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

### Signals em arquivo separado

Signals ficam em `signals.py` dentro da app e sao registrados via `apps.py`:

```python
# matches/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from matches.models import Match

@receiver(post_save, sender=Match)
def calculate_predictions_points(sender, instance, **kwargs):
    ...

# matches/apps.py
class MatchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matches'

    def ready(self):
        from matches import signals  # noqa: F401
```

### Forms com ModelForm

```python
class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['home_score', 'away_score']

    def clean(self):
        cleaned_data = super().clean()
        # validacoes aqui
        return cleaned_data
```

## HTML / Django Template Language

### Aspas simples em atributos HTML

```html
<!-- Certo -->
<a href='{% url "pool_list" %}' class='text-emerald-400 hover:text-emerald-300'>
    Meus Boloes
</a>

<!-- Errado -->
<a href="{% url "pool_list" %}" class="text-emerald-400 hover:text-emerald-300">
    Meus Boloes
</a>
```

### Heranca de templates

```html
{% extends 'base.html' %}
{% block content %}
    <!-- conteudo -->
{% endblock %}
```

### URLs nomeadas

```html
<!-- Certo - usar {% url %} -->
<a href='{% url "pool_detail" pool.pk %}'>Ver bolao</a>

<!-- Errado - nunca hardcodar URLs -->
<a href='/pools/1/'>Ver bolao</a>
```

### CSRF token

Todo form POST inclui `{% csrf_token %}`:

```html
<form method='post' action='{% url "prediction_create" pool_id=pool.pk match_id=match.pk %}'>
    {% csrf_token %}
    <!-- campos -->
</form>
```

### Texto em portugues

Todo texto visivel ao usuario em pt-BR:

```html
<h1 class='text-2xl font-bold text-white'>Meus Boloes</h1>
<p class='text-gray-400'>Voce ainda nao participa de nenhum bolao.</p>
```

## TailwindCSS

- Nenhum arquivo CSS separado. Tudo via classes utilitarias no HTML.
- Seguir o [design system](design-system.md) do projeto sem desvios.
- Nenhum `<script>` para logica de UI. Apenas JS nativo do browser quando estritamente necessario (ex: copiar texto para clipboard).

## Checklist pre-entrega

- [ ] Todo modelo tem `created_at` e `updated_at`
- [ ] Toda view e CBV com `LoginRequiredMixin`
- [ ] `get_queryset` filtra por `self.request.user` quando necessario
- [ ] Forms com ForeignKey filtram queryset pelo usuario logado
- [ ] Calculo de pontos so em `matches/signals.py`
- [ ] `apps.py` sobrescreve `ready()` para importar signals
- [ ] 100% aspas simples em Python e HTML
- [ ] PEP8 limpo
- [ ] Migracoes geradas e aplicadas
- [ ] Nenhum texto em ingles visivel ao usuario
- [ ] Nenhum URL hardcodado