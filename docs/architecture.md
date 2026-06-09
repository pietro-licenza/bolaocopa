# Arquitetura

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python + Django |
| Frontend | Django Template Language + TailwindCSS |
| Banco de dados | SQLite |
| Servidor dev | `runserver` |
| Servidor prod | Gunicorn |

Nenhum framework JavaScript. Nenhuma API REST. Nenhum DRF.

## Estrutura de diretorios

```
bolaocopa/
├── core/                  # Configuracoes globais do projeto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── matches/               # Selecoes, estadios, rodadas e jogos
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── live/                  # Integracao API-Football, eventos ao vivo (gols, cartoes, substituicoes)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── services/
│   │   └── api_football.py   # cliente HTTP da API-Football v3
│   ├── urls.py
│   ├── views.py
│   └── management/
│       └── commands/
│           └── backfill_match_external_ids.py
├── pools/                 # Boloes (criar, listar, convite, membros)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── predictions/           # Palpites dos usuarios nos jogos
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── rankings/              # Pontuacoes e classificacoes
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── users/                 # Usuarios (autenticacao por email)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/             # Templates globais do Django
│   ├── base.html
│   ├── pages/
│   ├── registration/
│   ├── matches/
│   ├── pools/
│   ├── predictions/
│   ├── rankings/
│   └── users/
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## Padroes arquiteturais

### Views

- **Sempre Class Based Views (CBV).** Nenhuma function-based view.
- Toda view autenticada usa `LoginRequiredMixin`.
- `get_queryset` filtra por `self.request.user` quando necessario.

### Templates

- Todos extendem `base.html` via `{% extends 'base.html' %}`.
- Todo conteudo vai dentro de `{% block content %}`.
- Estilizacao exclusivamente via TailwindCSS. Nenhum arquivo CSS separado.
- Todo texto visivel ao usuario em portugues brasileiro.

### Signals

- Ficam em `signals.py` dentro da app correspondente.
- Registrados via `apps.py` sobrescrevendo `ready()`.
- Calculo de pontos vive em `matches/signals.py` (disparado ao finalizar jogo).

### Forms

- `ModelForm` com validacao no backend.
- Dropdowns com `ForeignKey` filtram queryset pelo usuario logado.

### URLs

- Cada app tem seu proprio `urls.py`.
- Todas incluidas no `core/urls.py` via `path('<app>/', include('<app>.urls'))`.

### Configuracoes em `core/settings.py`

- `AUTH_USER_MODEL = 'users.CustomUser'`
- `LANGUAGE_CODE = 'pt-br'`
- `TIME_ZONE = 'America/Sao_Paulo'`
- `LOGIN_URL` e `LOGIN_REDIRECT_URL` configurados
- Templates directory aponta para `templates/` na raiz do projeto

### Integracao com API-Football (Sprint 7)

- Chave em `.env`: `API-FOOTBALL-KEY`
- Variaveis em settings: `API_FOOTBALL_KEY`, `API_FOOTBALL_BASE_URL` (default `https://v3.football.api-sports.io`), `API_FOOTBALL_LEAGUE_ID=1`, `API_FOOTBALL_SEASON=2026`
- Plano free: 100 req/dia. Rate-limit client-side via Django cache (LocMem) com contador diario; limite conservador de 95 req/dia
- `Match.external_id` mapeia para `fixture.id` da API
- `MatchEvent` (em `live/models.py`) armazena eventos (gols, cartoes, substituicoes) com minuto, jogador, time
- Sync por enquanto via botao manual; sync automatico por cron previsto para sprint futuro