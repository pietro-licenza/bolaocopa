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
  - [ ] Cadastrar 48 selecoes com nome oficial, codigo FIFA (3 letras) e confederacao
  - [ ] Incluir as 3 selecoes sedes: Canada, EUA, Mexico
  - [ ] Incluir as selecoes classificadas via eliminatorias ate o momento do seed
  - [ ] Verificar duplicatas pelo codigo FIFA antes de criar
  - [ ] Atualizar dados se a selecao ja existir (upsert)

**US-6.3: Popular estadios (Stadium)**
- **Como** administrador, **quero** cadastrar os estadios sede da Copa 2026, **para** que sejam exibidos nas paginas de jogos.
- **Criterios de aceite:**
  - [ ] Cadastrar 16 estadios sede da Copa 2026
  - [ ] Para cada estadio: nome, cidade, pais (EUA/Canada/Mexico) e capacidade
  - [ ] Verificar duplicatas pelo nome antes de criar
  - [ ] Atualizar dados se o estadio ja existir (upsert)

**US-6.4: Popular rodadas (Round)**
- **Como** administrador, **quero** cadastrar as fases/rodadas do torneio, **para** organizar e exibir os jogos agrupados.
- **Criterios de aceite:**
  - [ ] Cadastrar as 7 fases: Fase de Grupos, 32-avos (se aplicavel), Oitavas de Final, Quartas de Final, Semifinais, Disputa de 3o lugar, Final
  - [ ] Cada rodada com `name`, `order` (para ordenacao) e `start_date`/`end_date` (se aplicavel)
  - [ ] Ordenacao logica: Fase de Grupos (1), Oitavas (2), Quartas (3), Semis (4), 3o lugar (5), Final (6)
  - [ ] Verificar duplicatas pelo nome antes de criar

**US-6.5: Popular jogos da fase de grupos (Match)**
- **Como** administrador, **quero** cadastrar os 72 jogos da fase de grupos (12 grupos x 6 jogos), **para** que os usuarios possam palpitar desde o inicio do torneio.
- **Criterios de aceite:**
  - [ ] Cadastrar 72 jogos da fase de grupos com `home_team`, `away_team`, `stadium`, `round`, `match_datetime`
  - [ ] Agrupar corretamente os jogos em 12 grupos de 4 selecoes (A, B, C, ..., L)
  - [ ] Datas, horarios e locais conforme tabela oficial da FIFA
  - [ ] Todos os jogos com `status='agendado'` por padrao
  - [ ] Nenhum jogo pode ter `home_team == away_team`
  - [ ] Verificar duplicatas (`home_team`+`away_team`+`match_datetime`) antes de criar

**US-6.6: Popular jogos do mata-mata (Match)**
- **Como** administrador, **quero** cadastrar os jogos do mata-mata, **para** que o sistema tenha a tabela completa da Copa 2026.
- **Criterios de aceite:**
  - [ ] Cadastrar 32-avos de final (se aplicavel ao formato de 48 selecoes): 16 jogos
  - [ ] Cadastrar Oitavas de Final: 16 jogos
  - [ ] Cadastrar Quartas de Final: 8 jogos
  - [ ] Cadastrar Semifinais: 4 jogos
  - [ ] Cadastrar Disputa de 3o lugar: 1 jogo
  - [ ] Cadastrar Final: 1 jogo
  - [ ] Todos com `status='agendado'` por padrao
  - [ ] Datas, horarios e locais conforme calendario oficial

**US-6.VAL: Validacao do Sprint 6 — Seed da Copa 2026**
- **Como** agente de QA, **quero** validar todo o trabalho do Sprint 6, **para** garantir que o banco esta populado corretamente e o sistema consegue consumir os dados.
- **Criterios de aceite:**
  - [ ] Executar `python manage.py seed_world_cup_2026` em banco de teste
  - [ ] Validar contagens: 48 selecoes, 16 estadios, 7 rodadas, 104 jogos
  - [ ] Validar que nenhum jogo esta duplicado
  - [ ] Validar que o comando pode ser executado 2x sem duplicar nada
  - [ ] Validar listagem de jogos na UI: ordenacao por data, exibicao de selecoes/estadio/status
  - [ ] Validar que eh possivel registrar palpite em um jogo seedado
  - [ ] Corrigir bugs encontrados