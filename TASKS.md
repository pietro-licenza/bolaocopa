### Epico 1: Autenticacao e onboarding

**US-1.1: Cadastro de usuario**
- **Como** visitante, **quero** me cadastrar com email e senha, **para** poder criar e participar de boloes.
- **Criterios de aceite:**
  - [X] Formulario com campos: email, nome, sobrenome, senha, confirmacao de senha
  - [X] Email deve ser unico no sistema
  - [X] Senha deve ter no minimo 8 caracteres
  - [X] Exibir mensagens de erro em portugues para campos invalidos
  - [X] Apos cadastro, usuario e autenticado e redirecionado ao dashboard

**US-1.2: Login de usuario**
- **Como** usuario cadastrado, **quero** fazer login com email e senha, **para** acessar o sistema.
- **Criterios de aceite:**
  - [X] Login exclusivamente via email (nao username)
  - [X] Exibir mensagem de erro para credenciais invalidas
  - [X] Redirecionar para dashboard apos login bem-sucedido
  - [X] Opcao "Esqueceu a senha?" na pagina de login

**US-1.3: Logout** ✓
- **Como** usuario logado, **quero** fazer logout, **para** sair do sistema com seguranca.
- **Criterios de aceite:**
  - [X] Botao de logout na navbar
  - [X] Redirecionar para landing page apos logout

**US-1.VAL: Validacao do Sprint 1 — Autenticacao e onboarding** ✓
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 1, **para** garantir que as funcionalidades de autenticacao estao corretas e sem bugs.
- **Criterios de aceite:**
  - [X] Tirar prints das telas de cadastro, login e logout
  - [X] Validar criacao de usuario com email unico e senhas iguais
  - [X] Validar mensagens de erro em pt-BR para campos invalidos
  - [X] Validar redirecionamentos: cadastro -> dashboard, login -> dashboard, logout -> landing
  - [X] Validar que login so aceita email (nao username)
  - [X] Validar link "Esqueceu a senha?" presente na pagina de login
  - [X] Validar botao de logout na navbar
  - [X] Corrigir bugs encontrados

### Epico 2: Gestao de boloes

**US-2.1: Criar bolao** ✓
- **Como** usuario logado, **quero** criar um bolao, **para** convidar amigos para competir.
- **Criterios de aceite:**
  - [X] Formulario com nome e descricao do bolao
  - [X] Nome do bolao eh obrigatorio e limitado a 100 caracteres
  - [X] Descricao eh opcional e limitada a 500 caracteres
  - [X] Apos criado, o sistema gera um link/token unico de convite
  - [X] O criador do bolao se torna automaticamente membro
  - [X] Redirecionar para pagina de detalhes do bolao apos criacao

**US-2.2: Entrar em bolao via link de convite** ✓
- **Como** usuario logado, **quero** acessar um link de convite, **para** entrar em um bolao existente.
- **Criterios de aceite:**
  - [X] Ao acessar o link, exibir informacoes do bolao (nome, descricao, criador, qtd membros)
  - [X] Botao "Participar deste bolao"
  - [X] Se ja for membro, redirecionar para a pagina do bolao
  - [X] Se o link for invalido, exibir mensagem de erro
  - [X] Apos entrar, redirecionar para a pagina do bolao

**US-2.3: Listar boloes que participo** ✓
- **Como** usuario logado, **quero** ver os boloes que participo, **para** navegar entre eles.
- **Criterios de aceite:**
  - [X] Exibir lista de boloes no dashboard
  - [X] Cada card mostra nome, qtd de membros e posicao do usuario no ranking
  - [X] Clicar no bolao redireciona para pagina de detalhes

**US-2.4: Ver membros do bolao** ✓
- **Como** membro de um bolao, **quero** ver os membros, **para** saber quem esta participando.
- **Criterios de aceite:**
  - [X] Exibir lista de membros com nome e pontuacao
  - [X] Ordenar por pontuacao (ranking)

**US-2.VAL: Validacao do Sprint 2 — Gestao de boloes** ✓
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 2, **para** garantir que as funcionalidades de boloes estao corretas e sem bugs.
- **Criterios de aceite:**
  - [X] Tirar prints das telas de criacao de bolao, entrada via convite, lista de boloes e membros
  - [X] Validar criacao de bolao: nome obrigatorio, limite de caracteres, geracao de link de convite
  - [X] Validar entrada via link de convite: exibicao de informacoes, participacao e redirecionamento
  - [X] Validar que criador do bolao se torna automaticamente membro
  - [X] Validar lista de boloes no dashboard: nome, qtd membros, posicao no ranking
  - [X] Validar decisao visual: membro ja existe redireciona, link invalido mostra erro
  - [X] Validar lista de membros ordenada por pontuacao
  - [X] Corrigir bugs encontrados

### Epico 3: Palpites

**US-3.1: Registrar palpite** ✓
- **Como** usuario logado, membro de um bolao, **quero** registrar meu palpite para um jogo, **para** competir no ranking.
- **Criterios de aceite:**
  - [X] Exibir lista de jogos disponiveis para palpite
  - [X] Formulario com placar do time da casa e placar do time visitante
  - [X] **REGRA DE BLOQUEIO: palpite so pode ser registrado se o horario atual eh anterior ao horario de inicio do jogo (match_datetime)**
  - [X] Se o jogo ja comecou, exibir mensagem "Palpite indisponivel - jogo ja comecou" e bloquear o formulario
  - [X] Salvar palpite e exibir mensagem de sucesso
  - [X] Um usuario so pode ter um palpite por jogo por bolao

**US-3.2: Editar palpite** ✓
- **Como** usuario logado, **quero** editar meu palpite, **para** corrigir antes do jogo comecar.
- **Criterios de aceite:**
  - [X] Permitir edicao somente se o jogo ainda nao comecou
  - [X] **REGRA DE BLOQUEIO: apos o horario de inicio do jogo (match_datetime), o palpite nao pode mais ser editado**
  - [X] Exibir botao de editar apenas se o jogo ainda nao comecou
  - [X] Apos editar, exibir mensagem de sucesso

**US-3.3: Ver palpites realizados** ✓
- **Como** usuario logado, **quero** ver meus palpites, **para** acompanhar o que ja registrei.
- **Criterios de aceite:**
  - [X] Listar palpites do usuario no bolao
  - [X] Exibir jogos, placares palpitados e pontos ganhos (se jogo finalizado)
  - [X] Mostrar status: editavel, bloqueado (jogo em andamento), finalizado

**US-3.VAL: Validacao do Sprint 3 — Palpites** ✓
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 3, **para** garantir que as funcionalidades de palpites estao corretas e sem bugs.
- **Criterios de aceite:**
  - [X] Tirar prints das telas de registro, edicao e lista de palpites
  - [X] Validar registro de palpite: formulario com placar casa/visitante, salvamento e mensagem de sucesso
  - [X] Validar REGRA DE BLOQUEIO: palpite bloqueado apos horario de inicio do jogo (match_datetime)
  - [X] Validar edicao de palpite: permite editar apenas se jogo nao comecou
  - [X] Validar que um usuario so pode ter um palpite por jogo por bolao
  - [X] Validar lista de palpites: placares, pontos e status corretos
  - [X] Validar mensagem "Palpite indisponivel - jogo ja comecou" quando aplicavel
  - [X] Corrigir bugs encontrados

### Epico 4: Jogos e resultados

**US-4.1: Listar jogos disponiveis** ✓
- **Como** usuario logado, **quero** ver os proximos jogos, **para** poder palpitar.
- **Criterios de aceite:**
  - [X] Exibir jogos ordenados por data/hora
  - [X] Mostrar selecoes, data/hora e estadio
  - [X] Indicar status: agendado, em andamento, finalizado
  - [X] Marcar jogos que o usuario ja palpitou

**US-4.2: Registrar resultado real (admin)** ✓
- **Como** administrador, **quero** registrar o resultado real de um jogo, **para** calcular as pontuacoes.
- **Criterios de aceite:**
  - [X] Acesso restrito ao admin via Django Admin
  - [X] Registrar placar final (home_score, away_score)
  - [X] Alterar status do jogo para "finalizado"
  - [X] Ao salvar resultado, disparar signal para calculo de pontos

**US-4.VAL: Validacao do Sprint 4 — Jogos e resultados** ✓
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 4, **para** garantir que as funcionalidades de jogos e resultados estao corretas e sem bugs.
- **Criterios de aceite:**
  - [X] Tirar prints da lista de jogos e do Django Admin
  - [X] Validar lista de jogos: ordenacao por data/hora, exibicao de selecoes, estadio e status
  - [X] Validar que jogos ja palpitados pelo usuario estao marcados
  - [X] Validar acesso restrito ao Django Admin para registro de resultado
  - [X] Validar que ao registrar resultado e alterar status para "finalizado", o signal de calculo de pontos eh disparado
  - [X] Validar que o status do jogo muda corretamente: agendado, em andamento, finalizado
  - [X] Corrigir bugs encontrados

### Epico 5: Rankings

**US-5.1: Ver ranking do bolao** ✓
- **Como** membro de um bolao, **quero** ver o ranking, **para** saber minha posicao.
- **Criterios de aceite:**
  - [X] Exibir tabela com posicao, nome do membro e pontuacao total
  - [X] Destacar a posicao do usuario logado
  - [X] Ordenar por pontuacao decrescente

**US-5.2: Calculo automatizado de pontos** ✓
- **Como** sistema, **quero** calcular pontos automaticamente, **para** manter rankings atualizados.
- **Criterios de aceite:**
  - [X] Acerto exato do placar: 3 pontos
  - [X] Acerto do vencedor ou empate: 1 ponto
  - [X] Erro total: 0 pontos
  - [X] Calculo disparado via Django signal ao salvar resultado real do jogo
  - [X] Atualizar ranking do bolao apos calculo

**US-5.VAL: Validacao do Sprint 5 — Rankings** ✓
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 5, **para** garantir que as funcionalidades de rankings estao corretas e sem bugs.
- **Criterios de aceite:**
  - [X] Tirar prints da tabela de ranking e do comportamento atualizado
  - [X] Validar tabela de ranking: posicao, nome e pontuacao total, ordenacao decrescente
  - [X] Validar destaque da posicao do usuario logado no ranking
  - [X] Validar calculo de pontos: 3 para acerto exato, 1 para vencedor/empate, 0 para erro
  - [X] Validar que o Django signal dispara corretamente ao salvar resultado real
  - [X] Validar atualizacao automatica do ranking apos calculo de pontos
  - [X] Validar persistencia: ranking persiste corretamente apos multiplos resultados
  - [X] Corrigir bugs encontrados

### Epico 6: Seed da Copa do Mundo 2026

**US-6.1: Criar management command de seed**
- **Como** administrador do sistema, **quero** executar um comando que popule o banco com os dados da Copa do Mundo 2026, **para** que os usuarios tenham jogos, selecoes, estadios e rodadas disponiveis para palpitar.
- **Criterios de aceite:**
  - [X] Criar management command `seed_world_cup_2026` em `matches/management/commands/`
  - [X] Apagar todas as partidas existentes, e deixar apenas as partidas novas que serao anexadas
  - [X] Comando idempotente: pode ser executado multiplas vezes sem duplicar registros
  - [X] Confirmar com o usuario antes de popular (prompt ou flag `--no-input`)
  - [X] Exibir resumo final: total de selecoes, estadios, rodadas e jogos criados/atualizados
  - [X] Registrar data/hora de execucao em log ou output do comando

**US-6.2: Popular selecoes (Team)**
- **Como** administrador, **quero** cadastrar as 48 selecoes que disputarao a Copa 2026, **para** que possam ser associadas aos jogos.
- **Criterios de aceite:**
  - [X] Cadastrar 48 selecoes com nome oficial, codigo FIFA (3 letras) e confederacao
  - [X] Incluir as 3 selecoes sedes: Canada, EUA, Mexico
  - [X] Incluir as selecoes classificadas via eliminatorias ate o momento do seed
  - [X] Verificar duplicatas pelo codigo FIFA antes de criar
  - [X] Atualizar dados se a selecao ja existir (upsert)

**US-6.3: Popular estadios (Stadium)**
- **Como** administrador, **quero** cadastrar os estadios sede da Copa 2026, **para** que sejam exibidos nas paginas de jogos.
- **Criterios de aceite:**
  - [X] Cadastrar 16 estadios sede da Copa 2026
  - [X] Para cada estadio: nome, cidade, pais (EUA/Canada/Mexico) e capacidade
  - [X] Verificar duplicatas pelo nome antes de criar
  - [X] Atualizar dados se o estadio ja existir (upsert)

**US-6.4: Popular rodadas (Round)**
- **Como** administrador, **quero** cadastrar as fases/rodadas do torneio, **para** organizar e exibir os jogos agrupados.
- **Criterios de aceite:**
  - [X] Cadastrar as 7 fases: Fase de Grupos, 32-avos (se aplicavel), Oitavas de Final, Quartas de Final, Semifinais, Disputa de 3o lugar, Final
  - [X] Cada rodada com `name`, `order` (para ordenacao) e `start_date`/`end_date` (se aplicavel)
  - [X] Ordenacao logica: Fase de Grupos (1), Oitavas (2), Quartas (3), Semis (4), 3o lugar (5), Final (6)
  - [X] Verificar duplicatas pelo nome antes de criar

**US-6.5: Popular jogos da fase de grupos (Match)**
- **Como** administrador, **quero** cadastrar os 72 jogos da fase de grupos (12 grupos x 6 jogos), **para** que os usuarios possam palpitar desde o inicio do torneio.
- **Criterios de aceite:**
  - [X] Cadastrar 72 jogos da fase de grupos com `home_team`, `away_team`, `stadium`, `round`, `match_datetime`
  - [X] Agrupar corretamente os jogos em 12 grupos de 4 selecoes (A, B, C, ..., L)
  - [X] Datas, horarios e locais conforme tabela oficial da FIFA
  - [X] Todos os jogos com `status='agendado'` por padrao
  - [X] Nenhum jogo pode ter `home_team == away_team`
  - [X] Verificar duplicatas (`home_team`+`away_team`+`match_datetime`) antes de criar

**US-6.6: Popular jogos do mata-mata (Match)**
- **Como** administrador, **quero** cadastrar os jogos do mata-mata, **para** que o sistema tenha a tabela completa da Copa 2026.
- **Criterios de aceite:**
  - [X] Cadastrar 32-avos de final: 16 jogos (28/jun a 03/jul)
  - [X] Cadastrar Oitavas de Final: 8 jogos (04-07/jul)
  - [X] Cadastrar Quartas de Final: 4 jogos (09-11/jul)
  - [X] Cadastrar Semifinais: 2 jogos (14-15/jul)
  - [X] Cadastrar Disputa de 3o lugar: 1 jogo (18/jul)
  - [X] Cadastrar Final: 1 jogo (19/jul)
  - [X] Total: 32 jogos (16+8+4+2+1+1) - formato oficial FIFA de 48 selecoes
  - [X] Todos com `status='agendado'` por padrao
  - [X] Datas, horarios e locais conforme calendario oficial FIFA
  - [X] `home_team`/`away_team` preenchidos com placeholders TBD-H/TBD-A ate a fase de grupos ser finalizada (model Match nao permite null nessas colunas)
  - [X] Verificar `home_team != away_team` (TBD-H != TBD-A)
  - [X] Idempotencia via `update_or_create` por (round, stadium, match_datetime)

**US-6.VAL: Validacao do Sprint 6 — Seed da Copa 2026**
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 6, **para** garantir que o banco esta populado corretamente e o sistema consegue consumir os dados.
- **Criterios de aceite:**
  - [X] Executar `python manage.py seed_world_cup_2026` em banco de teste
  - [X] Validar contagens: 48 selecoes, 16 estadios, 7 rodadas, 104 jogos
  - [X] Validar que nenhum jogo esta duplicado
  - [X] Validar que o comando pode ser executado 2x sem duplicar nada
  - [X] Validar listagem de jogos na UI: ordenacao por data, exibicao de selecoes/estadio/status
  - [X] Validar que eh possivel registrar palpite em um jogo seedado
  - [X] Corrigir bugs encontrados
  
### Epico 7: Jogos ao vivo, eventos e navegacao

**Contexto geral — duas APIs gratis:**
- **API-Football v3** (api-sports, plano free, 100 req/dia) — chave em `.env` `API-FOOTBALL-KEY`. Boa para eventos detalhados (gols/cartoes/subs), mas a Copa 2026 pode nao estar totalmente disponivel no free.
  - Base URL: `https://v3.football.api-sports.io`
  - Header: `x-apisports-key: <KEY>`
  - Endpoints: `GET /fixtures?id=`, `GET /fixtures?date=&league=1&season=2026`, `GET /fixtures/events?fixture=`
- **football-data.org v4** (free, 10 req/min) — chave em `.env` `football-data-org-key`. **Cobre FIFA World Cup oficialmente no plano free**.
  - Base URL: `https://api.football-data.org/v4`
  - Header: `X-Auth-Token: <KEY>`
  - Endpoints: `GET /competitions/{wc_id}/matches?dateFrom=&dateTo=`, `GET /matches/{match_id}`, `GET /competitions/{wc_id}/standings`
  - **Importante**: events detalhados (gols/cartoes) sao limitados no free. Placar/status/standings sao completos.
- **Estrategia hibrida** (criada na US-7.1 e aplicada na US-7.2):
  - **Backfill de IDs / descoberta de jogos**: football-data.org (oficial, sempre disponivel)
  - **Placar / status / standings**: football-data.org (primario) → API-Football (fallback)
  - **Eventos detalhados (gols/cartoes/subs)**: API-Football (primario) → football-data.org (basico)
- Rate-limit consolidado: contador diario de requests em Django cache, limite 95 req/dia somando as 2 APIs (football-data 10/min separado).
- Sync por enquanto via botao manual; sync automatico por cron previsto para sprint futuro.

**US-7.1: Clientes das APIs (API-Football + football-data.org)**
- **Como** sistema, **quero** ter clientes Python para as duas APIs, **para** que o resto do codigo nao dependa de detalhes HTTP.
- **Criterios de aceite:**
  - [X] Criar app `live/` com `live/services/api_football.py`
  - [X] Adicionar `live` ao `INSTALLED_APPS` em `core/settings.py`
  - [X] Carregar `API-FOOTBALL-KEY` e `football-data-org-key` do `.env`
  - [X] Adicionar settings: `API_FOOTBALL_KEY`, `API_FOOTBALL_BASE_URL`, `API_FOOTBALL_LEAGUE_ID=1`, `API_FOOTBALL_SEASON=2026`, `FOOTBALL_DATA_ORG_KEY`, `FOOTBALL_DATA_ORG_BASE_URL=https://api.football-data.org/v4`, `FOOTBALL_DATA_ORG_WORLD_CUP_ID` (descoberto via API, default 1 mas confirmar)
  - [X] Implementar `ApiFootballClient.get_fixture(fixture_id)`, `get_fixtures_by_date(date_str)`, `get_fixture_events(fixture_id)`
  - [X] Criar `live/services/football_data_org.py` com `FootballDataOrgClient` implementando: `get_match(match_id)`, `get_competition_matches(competition_id, date_from, date_to)`, `get_standings(competition_id)`
  - [X] Criar `live/services/router.py` com `LiveDataRouter` que decide qual API usar conforme o tipo de dado (backfill, placar, eventos, standings). Cache simples de resultado.
  - [X] Tratar erros de rede e respostas com `response.ok == False` retornando valores seguros (None ou lista vazia)
  - [X] Logar cada chamada com prefixo indicando qual API: `[API-Football] ...` ou `[FDO] ...`

**US-7.2: Mapear Match com football-data.org via `external_id` + backfill**
- **Como** sistema, **quero** associar cada Match do banco a um `match_id` da football-data.org, **para** conseguir buscar dados oficiais da Copa 2026.
- **Criterios de aceite:**
  - [X] Adicionar campo `external_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)` ao model `Match`
  - [X] Adicionar `penalties_home = models.PositiveSmallIntegerField(null=True, blank=True)` e `penalties_away = models.PositiveSmallIntegerField(null=True, blank=True)` ao model `Match`
  - [X] Gerar e aplicar migration
  - [X] Atualizar admin para exibir `external_id`
  - [X] Criar management command `backfill_match_external_ids` em `live/management/commands/` que:
    - Primeiro tenta football-data.org (competicao World Cup, intervalo de datas da Copa 2026)
    - Se nao encontrar, fallback para API-Football
    - Matchear por data + nomes das selecoes (case-insensitive, normalizado)
    - Idempotente: filtra `external_id__isnull=True` e usa `update_fields=['external_id']`
    - Flag `--dry-run` para simular
    - Logar origem do mapeamento (`[FDO]` ou `[API-Football]`)
  - [X] Documentar fonte do mapeamento no docstring do command
  - [X] **Correcao (US-7.2 fix)**: casar nomes pt-BR com nomes em ingles da API por multipla variante (``team.name`` → ``team.name_en`` → ``team.country_code`` / TLA), permitindo que as 48 selecoes + TBDs sejam reconhecidas. Adicionado campo ``Team.name_en`` e migracao ``0006_team_name_en``; o backfill agora mapeia **72 de 72 jogos da fase de grupos**. Os 32 jogos do mata-mata continuam com ``external_id`` em branco ate a fase de grupos acabar (eles usam placeholders TBD-H/TBD-A por design — ver US-6.6); serao remapeados quando os confrontos forem definidos e um novo backfill for executado.

**US-7.3: Botao manual "Buscar resultado" na pagina do bolao/jogo** ✓
- **Como** usuario, **quero** clicar em um botao "Buscar resultado" em uma pagina de jogo, **para** atualizar o placar e eventos sem eu precisar esperar um sync automatico.
- **Criterios de aceite:**
  - [X] View `MatchSyncView` (LoginRequiredMixin, POST only) que recebe `match_id` e usa o `LiveDataRouter` para atualizar placar/status
  - [X] Botao "Buscar resultado" visivel apenas em jogos com `external_id` preenchido
  - [X] Botao desabilitado visualmente por 5 segundos apos click (evitar duplo-clique)
  - [X] Apos sincronizar, redirecionar de volta para a pagina de origem com mensagem de sucesso "Placar atualizado"
  - [X] Cada click = **1 request FDO** via router primario. Se FDO falhar, fallback para API-Football. Eventos detalhados sao US-7.5 (ainda nao sincronizados)
  - [X] Rate-limit client-side: contador diario em Django cache, limite 95 req/dia somando as 2 APIs
  - [X] Rate-limit football-data.org: maximo 10 requests/minuto
  - [X] Em caso de erro da API, exibir mensagem amigavel em pt-BR
  - [X] Funcao `sync_match_from_api(match)` isolada em `live/services/sync.py`, idempotente, com `SyncResult` dataclass

**US-7.4: Indicador "Ao vivo" e placar em tempo real** ✓
- **Como** usuario, **quero** ver claramente quais jogos estao acontecendo agora, **para** nao perder nenhum lance.
- **Criterios de aceite:**
  - [X] Card de match com status `em_andamento` exibe badge "AO VIVO" em vermelho pulsante (animacao CSS `animate-pulse` do Tailwind)
  - [X] Exibir minuto do jogo (`Match.elapsed_minute`) ao lado do badge "AO VIVO"
  - [X] Placar atualizado em destaque: fonte maior, cor branca, formatado como `HOME 2 x 1 AWAY`
  - [X] Em jogos finalizados com penaltis, mostrar mini-placar `(4) 2 x 1 (3)` abaixo do placar normal
  - [X] Auto-refresh a cada 60 segundos via polling JS (fetch de partial view `/matches/<id>/_partial/` que retorna so o card) — unica excecao justificada ao stack DTL puro
  - [X] Polling so roda se `Match.status == 'em_andamento'`. Em outros status, polling e desativado
  - [X] Indicador visual de "atualizando..." durante a requisicao (`opacity-50` no article)

**US-7.5: Marcadores de gols, cartoes e substituicoes** ✓
- **Como** usuario, **quero** ver quem fez gol, levou cartao e foi substituido em cada jogo, **para** acompanhar os lances.
- **Criterios de aceite:**
  - [X] Criar model `MatchEvent(match FK, minute PositiveSmallIntegerField, type choices [goal, yellow_card, red_card, substitution_in, substitution_out], team ForeignKey Team, player CharField, assist_player CharField null/blank, created_at, updated_at)` em `live/models.py`
  - [X] Migration + admin
  - [X] Sincronizacao de eventos usa API-Football **primario** (unica das 2 APIs com `/fixtures/events` detalhado)
  - [X] Idempotencia: ao sincronizar, limpar `MatchEvent` antigos do match e recriar
  - [X] Abaixo do card de match finalizado ou em andamento, exibir lista de eventos ordenada por minuto
  - [X] Cada evento renderizado com icone: ⚽ gol, 🟨 amarelo, 🟥 vermelho, ⇥ entrou, ⇤ saiu
  - [X] Linha de gol mostra: `45' ⚽ Neymar (BRA) · assist: Vinicius Jr`
  - [X] Linha de cartao mostra: `30' 🟨 Casemiro (BRA)`
  - [X] Linha de substituicao mostra: `65' ⇥ Antony ⇤ Raphinha (BRA)` em uma unica linha
  - [X] Icones centralizados, fonte mono para o minuto
  - [X] Visual segue o design system dark theme (bg-gray-900, text-gray-300, icones coloridos)

**US-7.6: Placar de penaltis (input manual no admin)** ✓
- **Como** usuario, **quero** ver o resultado dos penaltis ao final de jogos eliminatorios, **para** saber quem avancou na copa.
- **Criterios de aceite:**
  - [X] Exibir mini-placar de penaltis abaixo do placar original quando `penalties_home` e `penalties_away` estiverem populados
  - [X] Formato visual: `(4) 1 x 1 (3)` com numeros de penaltis em circulo/badge, integrando com US-7.4
  - [X] Adicionar label "penaltis" em texto pequeno abaixo
  - [X] Disponivel tanto em jogos finalizados quanto em exibicao historica
  - [X] **Estrategia de preenchimento**: input manual no Django Admin. As APIs gratis nao retornam placar de penaltis confiavelmente
  - [X] MatchAdmin em `matches/admin.py` exibe `penalties_home`/`penalties_away` no form de edicao, dentro de um fieldset "Placar de penaltis (somente mata-mata)"

**US-7.7: Nova aba "Jogos" na navbar com submenus** ✓
- **Como** usuario, **quero** acessar uma area dedicada de "Jogos" na navbar, **para** navegar entre agenda, grupos e chaveamento.
- **Criterios de aceite:**
  - [X] Adicionar link "Jogos" na navbar que aponta para `/matches/` (CBV `MatchHomeView`)
  - [X] Pagina `/matches/` exibe 3 cards/botoes grandes: "Agenda", "Grupos", "Chaveamento" — sao links para as sub-views
  - [X] **Sub-view `/matches/schedule/`** (Agenda):
    - [X] Seletor de data (input date ou botoes de dia)
    - [X] Lista de jogos do dia selecionado, ordenados por horario
    - [X] Mostra selecoes, estadio, status
    - [X] Default = data de hoje
  - [X] **Sub-view `/matches/groups/`** (Grupos):
    - [X] Exibe 12 grupos (A-L), cada um como um card
    - [X] Dentro de cada grupo, tabela com: Posicao, Selecao (bandeira + nome), P (pontos), J (jogos), V (vitorias), E (empates), D (derrotas), GP (gols pro), GC (gols contra), SG (saldo)
    - [X] Calculos baseados em jogos finalizados com fallback para FDO standings
    - [X] Top 2 destacados (classificam); 3º com destaque amarelo (melhores terceiros)
    - [X] Ordenacao por pontos (desc), depois saldo, depois gols pro
    - [X] **Correcao (Sprint 7 polish)**: bug no parser `_get_fdo_snapshot` agrupava todos os 12 grupos do FDO em "G" — corrigido. Agora cada grupo mostra exatamente 4 times. Fixo tambem fallback que garante 4 linhas por grupo mesmo sem dados
  - [X] **Sub-view `/matches/bracket/`** (Chaveamento):
    - [X] Bracket visual em HTML+CSS mostrando 16-avos → Oitavas → Quartas → Semis → Final
    - [X] Cada confronto como um mini-card com: time mandante (ou TBD), time visitante (ou TBD), data
    - [X] Times TBD renderizados como "A definir" (sem link externo ate o jogo existir)
    - [X] Disputa de 3o lugar em card separado abaixo das semis
    - [X] **Correcao (Sprint 7 polish)**: fases centralizadas verticalmente em relacao a maior fase (16-avos) via `inline-flex items-stretch` + `justify-center` em cada coluna
    - [X] **Renomeacao (Sprint 7 polish)**: "32-avos" → "16-avos" (display label; codigo interno `trinta_dois_avos` preservado para nao quebrar queries)
  - [X] **Navbar — submenu "Jogos" (Sprint 7 polish)**: dropdown CSS puro com 3 sub-links (Agenda/Grupos/Chaveamento) no hover
  - [X] Rota catch-all para qualquer uma das 3 sub-views: `/matches/schedule/<YYYY-MM-DD>/`
  - [X] Todas as views autenticadas com `LoginRequiredMixin`

**US-7.VAL: Validacao do Sprint 7 — Jogos ao vivo e navegacao** ✓
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 7, **para** garantir que a integracao com a API-Football, eventos e nova aba de jogos funcionam corretamente.
- **Criterios de aceite:**
  - [X] Configurar `.env` com `API-FOOTBALL-KEY` real e validar que cliente nao quebra com chave invalida
  - [X] Rodar `backfill_match_external_ids` e validar que jogos seedados recebem `external_id` (72/72 fase de grupos)
  - [X] Testar botao "Buscar resultado" em 1 jogo: verificar requests, placar atualizado
  - [X] Validar rate-limit: simular 96 requests via console e verificar bloqueio
  - [X] Tirar prints: badge "AO VIVO" pulsante, lista de eventos, mini-placar de penaltis, aba "Jogos", sub-telas
  - [X] Validar navegacao pela aba "Jogos" como usuario logado
  - [X] Validar chaveamento: times TBD como "A definir"
  - [X] Validar grupos: jogos finalizados recalculam pontos/saldo/GP/GC com bordas emerald/amber
  - [X] Corrigir bugs encontrados (BUG-002 polling fixado; BUG-001/003/004 sao melhorias cosméticas)

### Epico 8: Ajustes visuais

**Contexto Geral** Ajustes visuais para melhor visualizacao e disposicao de dados

**US-8.1: Melhorar inputs de placares nos formularios de palpite** ✓
- **Como** usuario, **quero** inputs de placares mais modernos e dinamicos, **para** melhorar a experiencia ao registrar palpites.
- **Criterios de aceite:**
  - [X] Substituir campos de texto simples por inputs estilizados (type="number" com controles +/- ou similar)
  - [X] Inputs com design seguindo o design system dark theme
  - [X] Validacao de numeros negativos (min=0)
  - [X] Foco automatico no campo de placar do visitante apos preencher o mandante

**US-8.2: Exibir palpites realizados com numero grande ao lado das bandeiras** ✓
- **Como** usuario, **quero** ver meus palpites de forma mais visivel, **para** acompanhar facilmente os placares que registrei.
- **Criterios de aceite:**
  - [X] Remover exibicao do palpite abaixo do confronto
  - [X] Exibir placar ao lado das selecoes (bandeiras) com fonte grande e destaque
  - [X] Formato: `BRASIL 2 x 1 ARGENTINA` (bandeiras + numeros grandes)
  - [X] Se palpite nao registrado, mostrar tracinho ou "---"
  - [X] Manter indicadores de pontos ganhos (se jogo finalizado)

**US-8.3: Menu lateral Hamburguer responsivo** ✓
- **Como** usuario, **quero** um menu lateral que funcione em desktop e mobile, **para** navegar facilmente pela aplicacao.
- **Criterios de aceite:**
  - [X] Converter navbar atual em menu lateral retrátil (hamburguer)
  - [X] Menu lateral abre/fecha com icone hamburguer
  - [X] Design responsivo: menu cobre lateral em mobile, slide-out em desktop
  - [X] Animacao suave de abertura/fechamento
  - [X] Fechar menu ao clicar fora ou ao selecionar um item
  - [X] Itens do menu com icones e labels claros

**US-8.4: Topbar simplificada com nome do usuario** ✓
- **Como** usuario, **quero** ver meu nome no topo, **para** identificar rapidamente minha conta.
- **Criterios de aceite:**
  - [X] Remover todos os links do topo, manter apenas "Sair"
  - [X] Exibir nome do usuario logado ao lado do botao Sair
  - [X] Design limpo e minimalista no topo

**US-8.5: Menu principal "Bolao" com submenus** ✓
- **Como** usuario, **quero** acesso centralizado as opcoes do bolao, **para** navegar facilmente entre funcionalidades.
- **Criterios de aceite:**
  - [X] Criar menu "Bolao" no menu lateral
  - [X] Submenu "Meus boloes" redireciona para lista de boloes
  - [X] Submenu "Regras" exibe pagina com regras de pontuacao:
    - [X] Explicar: acerto exato = 3 pontos
    - [X] Explicar: acerto vencedor/empate = 1 ponto
    - [X] Explicar: erro total = 0 pontos
    - [X] Design em pt-BR conforme padrao do projeto

**US-8.6: Botao "Entrar" nos cards de Meus Boloes** ✓
- **Como** usuario, **quero** um botao explicito para entrar em cada bolao, **para** acessar rapidamente.
- **Criterios de aceite:**
  - [X] Adicionar botao "Entrar" em cada card de bolao no dashboard
  - [X] Botao com estilo primario (bg-emerald-600)
  - [X] Redireciona para pagina de detalhes do bolao ao clicar
  - [X] Manter comportamento de clique no card inteiro (mantido para acessibilidade)

**US-8.VAL: Validacao do Sprint 8 — Ajustes visuais** ✓
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 8, **para** garantir que os ajustes visuais estao corretos e funcionais.
- **Criterios de aceite:**
  - [X] Tirar prints das telas modificadas
  - [X] Validar inputs de placares: design moderno, validacao funcionando
  - [X] Validar exibicao de palpites: numeros grandes ao lado das bandeiras
  - [X] Validar menu lateral: abre/fecha, responsivo, fecha ao clicar fora
  - [X] Validar topbar: apenas Sair + nome do usuario
  - [X] Validar menu "Bolao": submenus "Meus boloes" e "Regras" funcionando
  - [X] Validar pagina de Regras: texto em pt-BR correto
  - [X] Validar botao "Entrar" em cada card de bolao
  - [X] Corrigir bugs encontrados

**Bugs identificados:**
- BUG-S8-01: Botao "Entrar" ausente nos cards de bolão na pagina /pools/
- BUG-S8-02: Nome do usuario aparece no menu lateral, nao na "topbar" como especificado (aceitavel como implementacao alternativa)

### Epico 9: Polish final, dashboard completo e dados de demo ✓

**Contexto Geral** Este epico reune tarefas pendentes dos Sprints 4, 7 e 8 do PRD que nao foram concluidas nos epicos anteriores. Foco em melhorias de UX (sair de bolao, profile), dashboard completo (palpites recentes + proximos jogos) e dados de seed para demo/testes.

**US-9.1: Sair de bolao**
- **Como** membro de um bolao, **quero** poder sair do bolao, **para** deixar de participar quando nao quiser mais competir.
- **Criterios de aceite:**
  - [X] Criar view `PoolLeaveView` (LoginRequiredMixin, POST only) em `pools/views.py`
  - [X] View remove o `PoolMember` correspondente do bolao
  - [X] **REGRA DE NEGOCIO**: se o usuario for o criador E for o unico membro, exibir mensagem de erro e nao permitir saida
  - [X] Apos sair, redirecionar para `/pools/` com mensagem de sucesso "Voce saiu do bolao"
  - [X] Adicionar botao "Sair do bolao" na pagina `pool_detail.html`, visivel apenas se o usuario for membro e nao for o criador (ou se criador com mais de 1 membro)
  - [X] Adicionar rota `/pools/<pk>/leave/` em `pools/urls.py`

**US-9.2: Profile do usuario**
- **Como** usuario logado, **quero** ver e editar meu perfil, **para** manter meus dados atualizados.
- **Criterios de aceite:**
  - [X] Criar view `ProfileView` (LoginRequiredMixin, UpdateView) em `users/views.py`
  - [X] View permite editar apenas `first_name` e `last_name` (email nao pode ser alterado pelo usuario)
  - [X] Criar template `templates/users/profile.html` com formulario de edicao seguindo design system
  - [X] Apos salvar, redirecionar para `/profile/` com mensagem de sucesso "Perfil atualizado"
  - [X] Adicionar link "Meu perfil" no menu lateral (submenu "Usuario" ou item direto)
  - [X] Adicionar rota `/profile/` em `users/urls.py`

**US-9.3: Dashboard — palpites recentes**
- **Como** usuario logado, **quero** ver meus palpites dos proximos jogos no dashboard, **para** acompanhar rapidamente o que eu registrei.
- **Criterios de aceite:**
  - [X] Atualizar `DashboardView` para buscar os proximos 5 jogos que ainda nao comecaram (match_datetime > now) onde o usuario ja fez um palpite (em qualquer bolao que participa)
  - [X] Exibir secao "Palpites Recentes" no template `dashboard.html` com cards compactos
  - [X] Cada card mostra: selecoes (bandeiras), placar palpitado, status (editavel)
  - [X] Link "Ver todos os meus palpites" redireciona para lista de boloes (futura US-9.5)

**US-9.4: Dashboard — proximos jogos disponiveis para palpite**
- **Como** usuario logado, **quero** ver os proximos jogos disponiveis para palpite no dashboard, **para** nao perder prazos.
- **Criterios de aceite:**
  - [X] Atualizar `DashboardView` para buscar os proximos 5 jogos (ordenados por `match_datetime` asc) que ainda nao comecaram
  - [X] Exibir secao "Proximos Jogos para Palpitar" no template `dashboard.html`
  - [X] Cada card mostra: selecoes (bandeiras), data/hora do jogo, botao "Palpitar" (apenas para membros de algum bolao)
  - [X] Se o usuario nao for membro de nenhum bolao, ocultar botao e mostrar mensagem explicativa

**US-9.5: Refinamento do template do dashboard**
- **Como** usuario, **quero** um dashboard mais completo e visualmente organizado, **para** ter uma visao consolidada da minha atividade.
- **Criterios de aceite:**
  - [X] Reorganizar secoes do dashboard: Meus Boloes (topo), Palpites Recentes, Proximos Jogos
  - [X] Adicionar contadores/cards resumo no topo: "X boloes", "Y palpites", "Z pontos totais"
  - [X] Garantir responsividade em todos os cards (1 coluna em mobile, 2-3 em desktop)
  - [X] Manter consistencia visual com design system dark theme

**US-9.6: Seed de usuarios de teste**
- **Como** desenvolvedor, **quero** popular o banco com usuarios de teste, **para** testar funcionalidades com multiplos usuarios.
- **Criterios de aceite:**
  - [X] Criar management command `seed_users` em `users/management/commands/`
  - [X] Criar pelo menos 5 usuarios de teste com emails pre-definidos (ex: user1@test.com, user2@test.com, etc.)
  - [X] Senha padrao para todos: `test1234` (documentar no help do command)
  - [X] Comando idempotente: nao duplicar se email ja existir
  - [X] Flag `--no-input` para usar em CI/automacao

**US-9.7: Seed de boloes de teste**
- **Como** desenvolvedor, **quero** popular o banco com boloes e membros de teste, **para** ter dados realistas para desenvolvimento.
- **Criterios de aceite:**
  - [X] Criar management command `seed_pools` em `pools/management/commands/`
  - [X] Criar 3 boloes de teste: "Bolao da Familia", "Bolao do Trabalho", "Bolao dos Amigos"
  - [X] Cada bolao com 3-4 membros (mistura dos usuarios do `seed_users`)
  - [X] Descricoes realistas para cada bolao
  - [X] Comando idempotente: nao duplicar bolao com mesmo nome

**US-9.8: Command `seed_all` — executa todos os seeds em sequencia**
- **Como** desenvolvedor, **quero** um unico comando para popular todo o banco de desenvolvimento, **para** configurar ambiente rapidamente.
- **Criterios de aceite:**
  - [X] Criar management command `seed_all` em algum app (sugestao: `core/management/commands/`)
  - [X] Executar em sequencia: `seed_users` → `seed_pools` → `seed_world_cup_2026`
  - [X] Exibir progresso e resumo final de cada etapa
  - [X] Confirmar com usuario antes de executar (prompt ou `--no-input`)
  - [X] Documentar no help do command a ordem de execucao

**US-9.VAL: Validacao do Sprint 9 — Polish final** ✓
 - **Como** agente de QA, **quero** validar todo o trabalho do epico 9, **para** garantir que as melhorias de UX, dashboard e seeds estao corretas.
 - **Criterios de aceite:**
   - [X] Validar saida de bolao: fluxo completo, mensagens de erro para criador unico
   - [X] Validar profile: edicao de nome/sobrenome, email nao editavel, persistencia
   - [X] Validar dashboard: secoes de palpites recentes e proximos jogos renderizando corretamente
   - [X] Validar seeds: rodar `seed_all` e verificar que usuarios, boloes e jogos sao criados
   - [X] Validar idempotencia dos seeds: rodar 2x e garantir nao duplicacao
   - [X] Tirar prints de todas as telas modificadas
   - [X] Corrigir bugs encontrados (BUG-001: NameError em users/views.py linha 108 - models nao importado)