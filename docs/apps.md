# Apps do Django

Cada app isola um dominio do sistema. Nenhuma logica de negocio cruza apps sem necessidade.

---

## users

**Responsabilidade:** Usuario customizado com autenticacao por email.

| Arquivo | Funcao |
|---------|--------|
| `models.py` | `CustomUser` estendendo `AbstractUser` com `USERNAME_FIELD = 'email'` |
| `forms.py` | `CustomUserCreationForm`, `CustomUserChangeForm` |
| `views.py` | `RegisterView`, `LoginView`, `LogoutView`, `ProfileView` (todas CBV) |
| `urls.py` | `/register/`, `/login/`, `/logout/`, `/profile/` |
| `admin.py` | `CustomUserAdmin` estendendo `UserAdmin` |

### Modelo CustomUser

- `email` - `EmailField(unique=True)` - campo de login
- `first_name` - `CharField` - nome
- `last_name` - `CharField` - sobrenome
- `created_at` - `DateTimeField(auto_now_add=True)`
- `updated_at` - `DateTimeField(auto_now=True)`
- `username = None` - removido
- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = []`

---

## matches

**Responsabilidade:** Cadastro de selecoes, estadios, rodadas e jogos reais da Copa.

| Arquivo | Funcao |
|---------|--------|
| `models.py` | `Team`, `Stadium`, `Round`, `Match` |
| `views.py` | `MatchListView`, `MatchDetailView` (CBV) |
| `signals.py` | Signal `post_save` em `Match` para disparar calculo de pontos |
| `urls.py` | `/matches/`, `/matches/<pk>/` |
| `admin.py` | `ModelAdmin` com `list_display`, `search_fields`, `list_filter` |

### Modelo Team

- `name` - `CharField(max_length=100)`
- `country_code` - `CharField(max_length=3, unique=True)`
- `flag_emoji` - `CharField(max_length=10)`
- `created_at`, `updated_at`

### Modelo Stadium

- `name` - `CharField(max_length=200)`
- `city` - `CharField(max_length=100)`
- `country` - `CharField(max_length=100)`
- `created_at`, `updated_at`

### Modelo Round

- `name` - `CharField(max_length=100)`
- `order` - `PositiveIntegerField()`
- `phase` - `CharField(max_length=20, choices=...)` - valores: `grupo`, `oitavas`, `quartas`, `semi`, `terceiro_lugar`, `final`
- `created_at`, `updated_at`

### Modelo Match

- `round` - `ForeignKey(Round)`
- `stadium` - `ForeignKey(Stadium)`
- `home_team` - `ForeignKey(Team, related_name='home_matches')`
- `away_team` - `ForeignKey(Team, related_name='away_matches')`
- `match_datetime` - `DateTimeField()`
- `home_score` - `PositiveIntegerField(null=True, blank=True)`
- `away_score` - `PositiveIntegerField(null=True, blank=True)`
- `status` - `CharField(max_length=20, choices=...)` - valores: `agendado`, `em_andamento`, `finalizado`; default `agendado`
- `created_at`, `updated_at`

---

## pools

**Responsabilidade:** Criar boloes, gerar link de convite, gerenciar membros.

| Arquivo | Funcao |
|---------|--------|
| `models.py` | `Pool`, `PoolMember` |
| `forms.py` | `PoolForm` |
| `views.py` | `PoolCreateView`, `PoolListView`, `PoolDetailView`, `PoolJoinView`, `PoolLeaveView` |
| `urls.py` | `/pools/`, `/pools/create/`, `/pools/<pk>/`, `/pools/<pk>/join/`, `/pools/<pk>/leave/` |
| `admin.py` | `PoolAdmin`, `PoolMemberAdmin` |

### Modelo Pool

- `name` - `CharField(max_length=100)`
- `description` - `TextField(blank=True)`
- `invite_token` - `UUIDField(default=uuid.uuid4, unique=True)`
- `created_by` - `ForeignKey(CustomUser, related_name='created_pools')`
- `created_at`, `updated_at`

### Modelo PoolMember

- `pool` - `ForeignKey(Pool, related_name='members')`
- `user` - `ForeignKey(CustomUser, related_name='pool_memberships')`
- `joined_at` - `DateTimeField(auto_now_add=True)`
- `created_at`, `updated_at`
- `Meta.unique_together = ('pool', 'user')`

---

## predictions

**Responsabilidade:** Palpites dos usuarios nos jogos (placar A x placar B).

| Arquivo | Funcao |
|---------|--------|
| `models.py` | `Prediction` |
| `forms.py` | `PredictionForm` |
| `views.py` | `PredictionCreateView`, `PredictionUpdateView`, `PredictionListView` |
| `urls.py` | `/pools/<pool_id>/predictions/`, `/pools/<pool_id>/predictions/create/<match_id>/`, `/pools/<pool_id>/predictions/<pk>/edit/` |
| `admin.py` | `PredictionAdmin` |

### Modelo Prediction

- `user` - `ForeignKey(CustomUser, related_name='predictions')`
- `match` - `ForeignKey(Match, related_name='predictions')`
- `pool` - `ForeignKey(Pool, related_name='predictions')`
- `home_score` - `PositiveIntegerField()`
- `away_score` - `PositiveIntegerField()`
- `points` - `IntegerField(default=0)`
- `created_at`, `updated_at`
- `Meta.unique_together = ('user', 'match', 'pool')`

### Regra de bloqueio

- `PredictionCreateView` e `PredictionUpdateView` validam que `match.match_datetime > now()`.
- Se o jogo ja comecou, o formulario fica desabilitado e exibe mensagem de bloqueio.

---

## rankings

**Responsabilidade:** Pontuacoes gerais e tabelas de classificacao por bolao.

| Arquivo | Funcao |
|---------|--------|
| `models.py` | `Ranking` |
| `views.py` | `RankingListView`, `RankingGlobalView` |
| `urls.py` | `/pools/<pool_id>/ranking/`, `/rankings/global/` |
| `admin.py` | `RankingAdmin` |

### Modelo Ranking

- `user` - `ForeignKey(CustomUser, related_name='rankings')`
- `pool` - `ForeignKey(Pool, related_name='rankings')`
- `total_points` - `IntegerField(default=0)`
- `position` - `IntegerField(default=0)`
- `created_at`, `updated_at`
- `Meta.unique_together = ('user', 'pool')`

### Regra de pontuacao

Calculada via signal em `matches/signals.py` ao finalizar um jogo:

| Condicao | Pontos |
|----------|--------|
| Acerto exato do placar | 3 pontos |
| Acerto do vencedor ou empate | 1 ponto |
| Erro total | 0 pontos |

Apos o calculo, o `total_points` de cada `Ranking` eh atualizado e as posicoes sao recalculadas.