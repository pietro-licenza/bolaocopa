# Design System

Tema escuro obrigatorio em **todas** as telas. Nenhum modo claro.

---

## Paleta de cores

| Nome | TailwindCSS | Hex | Uso |
|------|------------|-----|-----|
| Fundo principal | `bg-gray-950` | #030712 | Background geral do site |
| Fundo card | `bg-gray-900` | #111827 | Cards, containers, modais |
| Fundo card hover | `bg-gray-800` | #1f2937 | Hover em cards e botoes |
| Borda sutil | `border-gray-700` | #374151 | Bordas de cards e inputs |
| Borda foco | `border-emerald-500` | #10b981 | Borda de input em foco |
| Texto principal | `text-white` | #ffffff | Titulos e textos principais |
| Texto secundario | `text-gray-400` | #9ca3af | Descricoes e labels |
| Texto terciario | `text-gray-500` | #6b7280 | Textos menos importantes |
| Verde primario | `text-emerald-400` | #34d399 | Acoes primarias, links, destaques |
| Verde hover | `text-emerald-300` | #6ee7b7 | Hover em acoes primarias |
| Verde bg botao | `bg-emerald-600` | #059669 | Background de botoes primarios |
| Verde hover botao | `hover:bg-emerald-500` | #10b981 | Hover de botoes primarios |
| Vermelho alerta | `text-red-400` | #f87171 | Erros, alertas |
| Amarelo destaque | `text-amber-400` | #fbbf24 | Pontuacao, rankings, medalhas |
| Azul info | `text-sky-400` | #38bdf8 | Informacoes, links secundarios |

---

## Tipografia

| Elemento | Classes TailwindCSS | Uso |
|----------|--------------------|----|
| H1 | `text-3xl md:text-4xl font-bold text-white` | Titulos principais de pagina |
| H2 | `text-2xl md:text-3xl font-semibold text-white` | Titulos de secao |
| H3 | `text-xl md:text-2xl font-semibold text-white` | Titulos de card |
| Corpo | `text-base text-gray-300` | Texto geral |
| Label | `text-sm font-medium text-gray-400` | Labels de formulario |
| Badge | `text-xs font-semibold uppercase tracking-wider` | Tags e badges |
| Numero/Placar | `text-4xl md:text-5xl font-bold text-white tabular-nums` | Placares de jogos |

---

## Gradientes

| Uso | Classes TailwindCSS |
|-----|--------------------|
| Hero banner | `bg-gradient-to-br from-gray-900 via-emerald-950 to-gray-900` |
| Card destaque | `bg-gradient-to-r from-emerald-600/10 to-transparent` |
| Background geral | `bg-gray-950 min-h-screen` |

---

## Grid e layout

| Elemento | Classes TailwindCSS |
|----------|--------------------|
| Container | `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` |
| Grid 3 colunas | `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6` |
| Grid 2 colunas | `grid grid-cols-1 md:grid-cols-2 gap-6` |
| Secao | `py-8 md:py-12` |

---

## Componentes

### Navbar

```html
<nav class='bg-gray-900/80 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50'>
    <div class='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
        <div class='flex items-center justify-between h-16'>
            <a href='/' class='text-emerald-400 font-bold text-xl'>BolaoCopa</a>
            <div class='flex items-center gap-4'>
                <!-- links de navegacao -->
            </div>
        </div>
    </div>
</nav>
```

### Botao primario

```html
<a href='#' class='inline-flex items-center justify-center px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition-colors duration-200'>
    Texto do Botao
</a>
```

### Botao secundario

```html
<a href='#' class='inline-flex items-center justify-center px-6 py-3 border border-gray-600 hover:border-emerald-500 text-gray-300 hover:text-emerald-400 font-semibold rounded-lg transition-colors duration-200'>
    Texto do Botao
</a>
```

### Card de jogo

```html
<div class='bg-gray-900 border border-gray-700 rounded-xl p-6 hover:border-emerald-500/50 transition-colors duration-200'>
    <div class='flex items-center justify-between'>
        <div class='flex flex-col items-center gap-2'>
            <span class='text-2xl'>🇧🇷</span>
            <span class='text-white font-semibold'>Brasil</span>
        </div>
        <div class='flex flex-col items-center gap-1'>
            <span class='text-xs text-gray-500 uppercase tracking-wider'>Fase de Grupos</span>
            <span class='text-4xl font-bold text-white tabular-nums'>2 x 1</span>
            <span class='text-sm text-gray-400'>12/06 16:00</span>
        </div>
        <div class='flex flex-col items-center gap-2'>
            <span class='text-2xl'>🇦🇷</span>
            <span class='text-white font-semibold'>Argentina</span>
        </div>
    </div>
</div>
```

### Card de ranking

```html
<div class='bg-gray-900 border border-gray-700 rounded-xl p-4 flex items-center justify-between'>
    <div class='flex items-center gap-4'>
        <span class='text-2xl font-bold text-amber-400'>#1</span>
        <span class='text-white font-semibold'>Nome do Usuario</span>
    </div>
    <div class='flex items-center gap-2'>
        <span class='text-emerald-400 font-bold'>42 pts</span>
    </div>
</div>
```

### Input de formulario

```html
<div>
    <label class='block text-sm font-medium text-gray-400 mb-1'>Label</label>
    <input type='text' class='w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none transition-colors duration-200' placeholder='Placeholder'>
</div>
```

### Mensagem de feedback

```html
<!-- Sucesso -->
<div class='bg-emerald-600/20 border border-emerald-500 text-emerald-400 px-4 py-3 rounded-lg'>
    Mensagem de sucesso.
</div>

<!-- Erro -->
<div class='bg-red-600/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg'>
    Mensagem de erro.
</div>
```

### Badge de status de jogo

```html
<!-- Agendado -->
<span class='text-xs font-semibold uppercase tracking-wider px-2 py-1 rounded-full bg-gray-700 text-gray-300'>Agendado</span>

<!-- Em andamento -->
<span class='text-xs font-semibold uppercase tracking-wider px-2 py-1 rounded-full bg-emerald-600/20 text-emerald-400'>Em andamento</span>

<!-- Finalizado -->
<span class='text-xs font-semibold uppercase tracking-wider px-2 py-1 rounded-full bg-amber-600/20 text-amber-400'>Finalizado</span>
```

---

## Regras

1. **Fundo escuro obrigatorio** em todas as telas - `bg-gray-950 min-h-screen` no body.
2. **Nenhum arquivo CSS separado** - tudo via TailwindCSS.
3. **Aspas simples** em todos os atributos HTML.
4. **Nenhum `<script>` para logica de UI** - apenas JS nativo quando estritamente necessario (ex: copiar para clipboard).
5. **Todo texto em pt-BR** nos templates.
6. **Todo link via `{% url %}`** - nunca hardcodar URLs.
7. **Todo form POST com `{% csrf_token %}`**.
8. **Responsivo** - testar em 375px (mobile) e 768px+ (desktop).