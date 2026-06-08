### Epico 1: Autenticacao e onboarding

**US-1.1: Cadastro de usuario**
- **Como** visitante, **quero** me cadastrar com email e senha, **para** poder criar e participar de boloes.
- **Criterios de aceite:**
  - [ ] Formulario com campos: email, nome, sobrenome, senha, confirmacao de senha
  - [ ] Email deve ser unico no sistema
  - [ ] Senha deve ter no minimo 8 caracteres
  - [ ] Exibir mensagens de erro em portugues para campos invalidos
  - [ ] Apos cadastro, usuario e autenticado e redirecionado ao dashboard

**US-1.2: Login de usuario**
- **Como** usuario cadastrado, **quero** fazer login com email e senha, **para** acessar o sistema.
- **Criterios de aceite:**
  - [ ] Login exclusivamente via email (nao username)
  - [ ] Exibir mensagem de erro para credenciais invalidas
  - [ ] Redirecionar para dashboard apos login bem-sucedido
  - [ ] Opcao "Esqueceu a senha?" na pagina de login

**US-1.3: Logout**
- **Como** usuario logado, **quero** fazer logout, **para** sair do sistema com seguranca.
- **Criterios de aceite:**
  - [ ] Botao de logout na navbar
  - [ ] Redirecionar para landing page apos logout

### Epico 2: Gestao de boloes

**US-2.1: Criar bolao**
- **Como** usuario logado, **quero** criar um bolao, **para** convidar amigos para competir.
- **Criterios de aceite:**
  - [ ] Formulario com nome e descricao do bolao
  - [ ] Nome do bolao eh obrigatorio e limitado a 100 caracteres
  - [ ] Descricao eh opcional e limitada a 500 caracteres
  - [ ] Apos criado, o sistema gera um link/token unico de convite
  - [ ] O criador do bolao se torna automaticamente membro
  - [ ] Redirecionar para pagina de detalhes do bolao apos criacao

**US-2.2: Entrar em bolao via link de convite**
- **Como** usuario logado, **quero** acessar um link de convite, **para** entrar em um bolao existente.
- **Criterios de aceite:**
  - [ ] Ao acessar o link, exibir informacoes do bolao (nome, descricao, criador, qtd membros)
  - [ ] Botao "Participar deste bolao"
  - [ ] Se ja for membro, redirecionar para a pagina do bolao
  - [ ] Se o link for invalido, exibir mensagem de erro
  - [ ] Apos entrar, redirecionar para a pagina do bolao

**US-2.3: Listar boloes que participo**
- **Como** usuario logado, **quero** ver os boloes que participo, **para** navegar entre eles.
- **Criterios de aceite:**
  - [ ] Exibir lista de boloes no dashboard
  - [ ] Cada card mostra nome, qtd de membros e posicao do usuario no ranking
  - [ ] Clicar no bolao redireciona para pagina de detalhes

**US-2.4: Ver membros do bolao**
- **Como** membro de um bolao, **quero** ver os membros, **para** saber quem esta participando.
- **Criterios de aceite:**
  - [ ] Exibir lista de membros com nome e pontuacao
  - [ ] Ordenar por pontuacao (ranking)

### Epico 3: Palpites

**US-3.1: Registrar palpite**
- **Como** usuario logado, membro de um bolao, **quero** registrar meu palpite para um jogo, **para** competir no ranking.
- **Criterios de aceite:**
  - [ ] Exibir lista de jogos disponiveis para palpite
  - [ ] Formulario com placar do time da casa e placar do time visitante
  - [ ] **REGRA DE BLOQUEIO: palpite so pode ser registrado se o horario atual eh anterior ao horario de inicio do jogo (match_datetime)**
  - [ ] Se o jogo ja comecou, exibir mensagem "Palpite indisponivel - jogo ja comecou" e bloquear o formulario
  - [ ] Salvar palpite e exibir mensagem de sucesso
  - [ ] Um usuario so pode ter um palpite por jogo por bolao

**US-3.2: Editar palpite**
- **Como** usuario logado, **quero** editar meu palpite, **para** corrigir antes do jogo comecar.
- **Criterios de aceite:**
  - [ ] Permitir edicao somente se o jogo ainda nao comecou
  - [ ] **REGRA DE BLOQUEIO: apos o horario de inicio do jogo (match_datetime), o palpite nao pode mais ser editado**
  - [ ] Exibir botao de editar apenas se o jogo ainda nao comecou
  - [ ] Apos editar, exibir mensagem de sucesso

**US-3.3: Ver palpites realizados**
- **Como** usuario logado, **quero** ver meus palpites, **para** acompanhar o que ja registrei.
- **Criterios de aceite:**
  - [ ] Listar palpites do usuario no bolao
  - [ ] Exibir jogos, placares palpitados e pontos ganhos (se jogo finalizado)
  - [ ] Mostrar status: editavel, bloqueado (jogo em andamento), finalizado

### Epico 4: Jogos e resultados

**US-4.1: Listar jogos disponiveis**
- **Como** usuario logado, **quero** ver os proximos jogos, **para** poder palpitar.
- **Criterios de aceite:**
  - [ ] Exibir jogos ordenados por data/hora
  - [ ] Mostrar selecoes, data/hora e estadio
  - [ ] Indicar status: agendado, em andamento, finalizado
  - [ ] Marcar jogos que o usuario ja palpitou

**US-4.2: Registrar resultado real (admin)**
- **Como** administrador, **quero** registrar o resultado real de um jogo, **para** calcular as pontuacoes.
- **Criterios de aceite:**
  - [ ] Acesso restrito ao admin via Django Admin
  - [ ] Registrar placar final (home_score, away_score)
  - [ ] Alterar status do jogo para "finalizado"
  - [ ] Ao salvar resultado, disparar signal para calculo de pontos

### Epico 5: Rankings

**US-5.1: Ver ranking do bolao**
- **Como** membro de um bolao, **quero** ver o ranking, **para** saber minha posicao.
- **Criterios de aceite:**
  - [ ] Exibir tabela com posicao, nome do membro e pontuacao total
  - [ ] Destacar a posicao do usuario logado
  - [ ] Ordenar por pontuacao decrescente

**US-5.2: Calculo automatizado de pontos**
- **Como** sistema, **quero** calcular pontos automaticamente, **para** manter rankings atualizados.
- **Criterios de aceite:**
  - [ ] Acerto exato do placar: 3 pontos
  - [ ] Acerto do vencedor ou empate: 1 ponto
  - [ ] Erro total: 0 pontos
  - [ ] Calculo disparado via Django signal ao salvar resultado real do jogo
  - [ ] Atualizar ranking do bolao apos calculo