# Agentes de IA - BolaoCopa

Agentes especializados para o projeto BolaoCopa. Cada agente opera em um dominio tecnico especifico da stack.

## Indice

| Agente | Arquivo | Especialidade | Quando usar |
|--------|---------|--------------|-------------|
| Django Backend | `django-backend.md` | Models, views, signals, forms, URLs, auth, migrations | Criar ou alterar modelos, views CBV, signals, forms, config do Django |
| DTL + TailwindCSS Frontend | `dtl-tailwind-frontend.md` | Templates DTL, estilizacao TailwindCSS, design system | Criar ou alterar templates HTML, paginas publicas, forms visuais, dashboard |
| QA / Playwright Validator | `qa-playwright-validator.md` | Testes funcionais e visuais end-to-end via navegador real | Validar funcionalidade e design de telas implementadas |

## Quando usar cada agente

### Django Backend
- Criar modelos (CustomUser, Team, Match, Pool, Prediction, Ranking)
- Implementar views CBV com LoginRequiredMixin
- Escrever signals (`matches/signals.py` para calculo de pontos)
- Configurar auth por email, forms, URLs
- Criar e aplicar migracoes
- Configurar `core/settings.py`

### DTL + TailwindCSS Frontend
- Criar ou refatorar `base.html`, landing page, login, registro, dashboard
- Criar templates de list/detail/form para cada app
- Aplicar o design system (dark theme, paleta emerald/gray)
- Garantir responsividade mobile-first
- Garantir aspas simples em atributos HTML e pt-BR nos textos visiveis

### QA / Playwright Validator
- Apos implementacao de uma feature pelo backend ou frontend
- Validar que auth por email funciona (login com username deve falhar)
- Validar bloqueio de palpites apos inicio do jogo
- Verificar consistencia visual com o design system
- Validar responsividade em mobile e desktop
- Antes de fechar uma sprint

## Ordem tipica de invocacao

1. **Django Backend** implementa modelos, views, forms, signals, URLs
2. **DTL + TailwindCSS Frontend** cria/refina os templates visuais
3. **QA / Playwright Validator** valida funcionalidade e design no navegador

## Fontes de referencia

- `PRD.md` — requisitos completos, modelo de dados, sprints
- `AGENTS.md` — convencoes criticas do projeto
- `docs/architecture.md` — stack, estrutura, padroes
- `docs/apps.md` — modelos e views por app
- `docs/database.md` — diagrama ER e regras de integridade
- `docs/code-style.md` — convencoes de codigo e checklist
- `docs/design-system.md` — paleta, tipografia, componentes