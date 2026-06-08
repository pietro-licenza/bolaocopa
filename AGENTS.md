# AGENTS.md

Project-specific guidance for working on BolaoCopa.

## Project identity

- **Name:** BolaoCopa — World Cup betting pool app
- **Stack:** Python 3.14 / Django 6.0.6 / SQLite / TailwindCSS (CDN) / Django Template Language
- **No REST API, no DRF, no JavaScript framework.** Full-stack Django with DTL only.

## Setup

```bash
source .venv/bin/activate
python manage.py runserver       # dev server at http://127.0.0.1:8000/
python manage.py makemigrations <app> && python manage.py migrate  # after model changes
```

No Docker. No test runner configured yet (planned for later sprints).

## Architecture

- `core/` — Django project config (settings, urls, wsgi). Not an app.
- App domains (each a Django app, not yet created):
  - `users/` — CustomUser with email login (`USERNAME_FIELD = 'email'`, `username = None`)
  - `matches/` — Team, Stadium, Round, Match models
  - `pools/` — Pool and PoolMember models
  - `predictions/` — Prediction model + `signals.py` for point calculation
  - `rankings/` — Ranking model
- Templates live in root-level `templates/` directory, organized by app subdirectory.
- `AUTH_USER_MODEL = 'users.CustomUser'` must be set in `core/settings.py` before first migration.

## Critical conventions

### Single quotes everywhere
Python strings and HTML attributes use single quotes. Double quotes only when syntax requires it.

```python
# Right
name = models.CharField(max_length=100)
# Wrong
name = models.CharField(max_length=100)
```

```html
<!-- Right -->
<a href='{% url "pool_list" %}' class='text-emerald-400'>Meus Boloes</a>
<!-- Wrong -->
<a href="{% url "pool_list" %}" class="text-emerald-400">Meus Bolões</a>
```

### Views: CBVs only, no function-based views
Every authenticated view must use `LoginRequiredMixin` as the first mixin.

```python
class PoolCreateView(LoginRequiredMixin, CreateView):
    ...
```

### Models: audit fields mandatory
Every model without exception must have:

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

### Auth: email, not username
CustomUser extends AbstractUser with `username = None`, `email` as `USERNAME_FIELD`, `REQUIRED_FIELDS = []`.

### Signals: separate file, registered via apps.py
Signal handlers live in `<app>/signals.py`. Each `apps.py` overrides `ready()` to import them.

```python
# matches/apps.py
class MatchesConfig(AppConfig):
    def ready(self):
        from matches import signals  # noqa: F401
```

Point calculation logic lives in `matches/signals.py`, triggered on `Match` status change to `finalizado`. Never in views or forms.

### Templates
- All extend `base.html` via `{% extends 'base.html'' %}`
- Content inside `{% block content %}`
- All user-visible text in **pt-BR** (in templates, not views)
- All URLs via `{% url 'name' %}` — never hardcode
- All POST forms include `{% csrf_token %}`
- No separate CSS files — TailwindCSS utility classes only in HTML

### Language split
- **Code** (identifiers, comments, variable names): English
- **UI text** (labels, headings, buttons, messages): Portuguese (pt-BR), lives in templates only

## Design system (dark theme)

| Element | Classes |
|---------|---------|
| Background | `bg-gray-950 min-h-screen` |
| Card | `bg-gray-900 border border-gray-700 rounded-xl p-6` |
| Card hover | `hover:border-emerald-500/50` |
| Primary button | `bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg` |
| Secondary button | `border border-gray-600 hover:border-emerald-500 text-gray-300` |
| Input | `bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white focus:border-emerald-500` |
| Label | `text-sm font-medium text-gray-400` |
| Heading H1 | `text-3xl md:text-4xl font-bold text-white` |
| Success msg | `bg-emerald-600/20 border border-emerald-500 text-emerald-400` |
| Error msg | `bg-red-600/20 border border-red-500 text-red-400` |

Full component reference: `docs/design-system.md`

## Key settings to configure (not yet in settings.py)

These are planned per PRD but not yet applied to `core/settings.py`:

```
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
```

Do not run `makemigrations` for `users` app until `AUTH_USER_MODEL` is set.

## Scoring rules (for signals)

| Condition | Points |
|-----------|--------|
| Exact score match | 3 |
| Correct winner or draw | 1 |
| Wrong | 0 |

Calculated in `matches/signals.py` when a Match status becomes `finalizado`. Then updates `Ranking.total_points` and recalculates `Ranking.position`.

## Prediction lock rule

Predictions can only be created/edited when `match.match_datetime > now()`. This validation must happen server-side in the view, not only in templates.

## File references

- `PRD.md` — full product requirements, data model, sprints
- `docs/architecture.md` — stack, directory structure, patterns
- `docs/apps.md` — per-app models, views, URLs
- `docs/database.md` — ER diagram, integrity rules
- `docs/code-style.md` — code conventions and pre-delivery checklist
- `docs/design-system.md` — colors, typography, component markup