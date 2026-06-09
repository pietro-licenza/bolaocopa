"""Seeder dos 32 jogos do mata-mata da Copa do Mundo FIFA 2026.

Formato oficial (aprovado pelo FIFA Council em 14 de marco de 2023):
48 selecoes na fase de grupos, com 12 grupos (A-L) de 4. Classificam-se
para o mata-mata os 2 primeiros de cada grupo + os 8 melhores terceiros
(32 times no total), em chave de eliminacao simples ate a final.

Total de jogos do mata-mata: 32
- 16-avos de Final (Round of 32): 16 jogos
- Oitavas de Final (Round of 16): 8 jogos
- Quartas de Final (Quarterfinals): 4 jogos
- Semifinais (Semifinals): 2 jogos
- Disputa de 3o Lugar: 1 jogo
- Final: 1 jogo
Total: 16 + 8 + 4 + 2 + 1 + 1 = 32 jogos.

Fontes consultadas (via webfetch):
- Tabela oficial do mata-mata: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage
  (revisao de junho de 2026). Inclui datas, horarios locais, estdios e
  combinacoes de cruzamentos para os 16-avos.
- Calendario oficial FIFA: https://digitalhub.fifa.com/m/1be9ce37eb98fcc5/
  original/FWC26-Match-Schedule_English.pdf (PDF publicado em 4/fev/2024).
- Regulamento oficial: https://digitalhub.fifa.com/m/636f5c9c6f29771f/
  original/FWC2026_regulations_EN.pdf (PDF, maio/2025), Anexo C com as
  495 combinacoes possiveis de terceiros classificados para os 16-avos.

Limitacao importante: as selecoes que disputam o mata-mata so sao
conhecidas apos o termino da fase de grupos (que ocorre em 27/jun/2026).
Como o seeder precisa ser executado antes desse termino (e talvez nem
todos os grupos tenham seus jogos finalizados ate la), NAO temos como
definir `home_team` e `away_team` dos jogos do mata-mata no momento da
seed.

Estrategia adotada: o model `Match` exige `home_team` e `away_team` como
`ForeignKey(Team)` NOT NULL. Em vez de uma migration para permitir
`null=True` nessas colunas (o que afetaria todos os jogos e quebraria
a UI), a US-6.6 cria DOIS registros `Team` placeholders
(`country_code` = 'TBD-H' e 'TBD-A', nomes "A definir (mandante)" e
"A definir (visitante)") que sao usados como `home_team` e `away_team`
em todos os 32 jogos do mata-mata. Isso garante:
- `home_team != away_team` (TBD-H != TBD-A).
- Model Match permanece inalterado (sem migration estrutural).
- Quando a fase de grupos for finalizada e os cruzamentos do mata-mata
  forem definidos, basta atualizar os campos `home_team`/`away_team`
  dos registros correspondentes.

Datas, horarios e estadios:
Os horarios locais (publicados pela FIFA) foram convertidos para UTC
para preencher `match_datetime` corretamente, independente do fuso
configurado no projeto (TIME_ZONE = 'America/Sao_Paulo').

Cada entrada da lista e uma tupla com:
- match_number: numero oficial da partida (73 a 104), conforme FIFA.
- round_name: nome da fase (deve existir em matches.models.Round).
- stadium_name: nome oficial do estadio (deve existir em matches.models.Stadium).
- utc_datetime: datetime aware em UTC do kick-off.
"""

import datetime

from django.utils import timezone

from matches.models import Match, Round, Stadium


# Lista ordenada por fase (ordem cronologica) e depois por data/hora.
# Origem primaria: tabela oficial do mata-mata publicada pela FIFA e
# conferida no artigo "2026 FIFA World Cup knockout stage" da Wikipedia en
# (revisao de junho de 2026). Match numbers 73-104 conforme numeracao FIFA.
WORLD_CUP_2026_KNOCKOUT_MATCHES = [
    # ===== 16-avos de Final (16 jogos, 28/jun a 03/jul) =====
    # Match 73: 2A vs 2B | 28/jun 12:00 local (UTC-7) = 19:00 UTC
    (73, '16-avos de Final', 'SoFi Stadium',
     datetime.datetime(2026, 6, 28, 19, 0, tzinfo=datetime.timezone.utc)),
    # Match 74: 1E vs 3 ABCDF | 29/jun 16:30 local (UTC-4) = 20:30 UTC
    (74, '16-avos de Final', 'Gillette Stadium',
     datetime.datetime(2026, 6, 29, 20, 30, tzinfo=datetime.timezone.utc)),
    # Match 75: 1F vs 2C | 29/jun 19:00 local (UTC-6) = 30/jun 01:00 UTC
    (75, '16-avos de Final', 'Estadio BBVA',
     datetime.datetime(2026, 6, 30, 1, 0, tzinfo=datetime.timezone.utc)),
    # Match 76: 1C vs 2F | 29/jun 12:00 local (UTC-5) = 17:00 UTC
    (76, '16-avos de Final', 'NRG Stadium',
     datetime.datetime(2026, 6, 29, 17, 0, tzinfo=datetime.timezone.utc)),
    # Match 77: 1I vs 3 CDFGH | 30/jun 17:00 local (UTC-4) = 21:00 UTC
    (77, '16-avos de Final', 'MetLife Stadium',
     datetime.datetime(2026, 6, 30, 21, 0, tzinfo=datetime.timezone.utc)),
    # Match 78: 2E vs 2I | 30/jun 12:00 local (UTC-5) = 17:00 UTC
    (78, '16-avos de Final', 'AT&T Stadium',
     datetime.datetime(2026, 6, 30, 17, 0, tzinfo=datetime.timezone.utc)),
    # Match 79: 1A vs 3 CEFHI | 30/jun 19:00 local (UTC-6) = 01/jul 01:00 UTC
    (79, '16-avos de Final', 'Estadio Azteca',
     datetime.datetime(2026, 7, 1, 1, 0, tzinfo=datetime.timezone.utc)),
    # Match 80: 1L vs 3 EHIJK | 01/jul 12:00 local (UTC-4) = 16:00 UTC
    (80, '16-avos de Final', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 7, 1, 16, 0, tzinfo=datetime.timezone.utc)),
    # Match 81: 1D vs 3 BEFIJ | 01/jul 17:00 local (UTC-7) = 02/jul 00:00 UTC
    (81, '16-avos de Final', "Levi's Stadium",
     datetime.datetime(2026, 7, 2, 0, 0, tzinfo=datetime.timezone.utc)),
    # Match 82: 1G vs 3 AEHIJ | 01/jul 13:00 local (UTC-7) = 20:00 UTC
    (82, '16-avos de Final', 'Lumen Field',
     datetime.datetime(2026, 7, 1, 20, 0, tzinfo=datetime.timezone.utc)),
    # Match 83: 2K vs 2L | 02/jul 19:00 local (UTC-4) = 23:00 UTC
    (83, '16-avos de Final', 'BMO Field',
     datetime.datetime(2026, 7, 2, 23, 0, tzinfo=datetime.timezone.utc)),
    # Match 84: 1H vs 2J | 02/jul 12:00 local (UTC-7) = 19:00 UTC
    (84, '16-avos de Final', 'SoFi Stadium',
     datetime.datetime(2026, 7, 2, 19, 0, tzinfo=datetime.timezone.utc)),
    # Match 85: 1B vs 3 EFG IJ | 02/jul 20:00 local (UTC-7) = 03/jul 03:00 UTC
    (85, '16-avos de Final', 'BC Place',
     datetime.datetime(2026, 7, 3, 3, 0, tzinfo=datetime.timezone.utc)),
    # Match 86: 1J vs 2H | 03/jul 18:00 local (UTC-4) = 22:00 UTC
    (86, '16-avos de Final', 'Hard Rock Stadium',
     datetime.datetime(2026, 7, 3, 22, 0, tzinfo=datetime.timezone.utc)),
    # Match 87: 1K vs 3 DEIJL | 03/jul 20:30 local (UTC-5) = 04/jul 01:30 UTC
    # Observacao: 03/jul 20:30 local em Kansas City (UTC-5) = 04/jul 01:30 UTC.
    # Esse jogo cai tecnicamente em 04/jul, mas a FIFA classifica como
    # "3 July 2026" no calendario oficial. Mantemos o horario UTC correto.
    (87, '16-avos de Final', 'Arrowhead Stadium',
     datetime.datetime(2026, 7, 4, 1, 30, tzinfo=datetime.timezone.utc)),
    # Match 88: 2D vs 2G | 03/jul 13:00 local (UTC-5) = 18:00 UTC
    (88, '16-avos de Final', 'AT&T Stadium',
     datetime.datetime(2026, 7, 3, 18, 0, tzinfo=datetime.timezone.utc)),
    # ===== Oitavas de Final (8 jogos, 04-07/jul) =====
    # Match 89: V73 vs V77 | 04/jul 17:00 local (UTC-4) = 21:00 UTC
    (89, 'Oitavas de Final', 'Lincoln Financial Field',
     datetime.datetime(2026, 7, 4, 21, 0, tzinfo=datetime.timezone.utc)),
    # Match 90: V73 vs V75 | 04/jul 12:00 local (UTC-5) = 17:00 UTC
    (90, 'Oitavas de Final', 'NRG Stadium',
     datetime.datetime(2026, 7, 4, 17, 0, tzinfo=datetime.timezone.utc)),
    # Match 91: V76 vs V78 | 05/jul 16:00 local (UTC-4) = 20:00 UTC
    (91, 'Oitavas de Final', 'MetLife Stadium',
     datetime.datetime(2026, 7, 5, 20, 0, tzinfo=datetime.timezone.utc)),
    # Match 92: V79 vs V80 | 05/jul 18:00 local (UTC-6) = 06/jul 00:00 UTC
    (92, 'Oitavas de Final', 'Estadio Azteca',
     datetime.datetime(2026, 7, 6, 0, 0, tzinfo=datetime.timezone.utc)),
    # Match 93: V83 vs V84 | 06/jul 14:00 local (UTC-5) = 19:00 UTC
    (93, 'Oitavas de Final', 'AT&T Stadium',
     datetime.datetime(2026, 7, 6, 19, 0, tzinfo=datetime.timezone.utc)),
    # Match 94: V81 vs V82 | 06/jul 17:00 local (UTC-7) = 07/jul 00:00 UTC
    (94, 'Oitavas de Final', 'Lumen Field',
     datetime.datetime(2026, 7, 7, 0, 0, tzinfo=datetime.timezone.utc)),
    # Match 95: V86 vs V88 | 07/jul 12:00 local (UTC-4) = 16:00 UTC
    (95, 'Oitavas de Final', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 7, 7, 16, 0, tzinfo=datetime.timezone.utc)),
    # Match 96: V85 vs V87 | 07/jul 13:00 local (UTC-7) = 20:00 UTC
    (96, 'Oitavas de Final', 'BC Place',
     datetime.datetime(2026, 7, 7, 20, 0, tzinfo=datetime.timezone.utc)),
    # ===== Quartas de Final (4 jogos, 09-11/jul) =====
    # Match 97: V89 vs V90 | 09/jul 16:00 local (UTC-4) = 20:00 UTC
    (97, 'Quartas de Final', 'Gillette Stadium',
     datetime.datetime(2026, 7, 9, 20, 0, tzinfo=datetime.timezone.utc)),
    # Match 98: V93 vs V94 | 10/jul 12:00 local (UTC-7) = 19:00 UTC
    (98, 'Quartas de Final', 'SoFi Stadium',
     datetime.datetime(2026, 7, 10, 19, 0, tzinfo=datetime.timezone.utc)),
    # Match 99: V91 vs V92 | 11/jul 17:00 local (UTC-4) = 21:00 UTC
    (99, 'Quartas de Final', 'Hard Rock Stadium',
     datetime.datetime(2026, 7, 11, 21, 0, tzinfo=datetime.timezone.utc)),
    # Match 100: V95 vs V96 | 11/jul 20:00 local (UTC-5) = 12/jul 01:00 UTC
    (100, 'Quartas de Final', 'Arrowhead Stadium',
     datetime.datetime(2026, 7, 12, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Semifinais (2 jogos, 14-15/jul) =====
    # Match 101: V97 vs V98 | 14/jul 14:00 local (UTC-5) = 19:00 UTC
    (101, 'Semifinal', 'AT&T Stadium',
     datetime.datetime(2026, 7, 14, 19, 0, tzinfo=datetime.timezone.utc)),
    # Match 102: V99 vs V100 | 15/jul 15:00 local (UTC-4) = 19:00 UTC
    (102, 'Semifinal', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 7, 15, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Disputa de 3o Lugar (1 jogo, 18/jul) =====
    # Match 103: P101 vs P102 | 18/jul 17:00 local (UTC-4) = 21:00 UTC
    (103, 'Disputa de 3o Lugar', 'Hard Rock Stadium',
     datetime.datetime(2026, 7, 18, 21, 0, tzinfo=datetime.timezone.utc)),
    # ===== Final (1 jogo, 19/jul) =====
    # Match 104: V101 vs V102 | 19/jul 15:00 local (UTC-4) = 19:00 UTC
    (104, 'Final', 'MetLife Stadium',
     datetime.datetime(2026, 7, 19, 19, 0, tzinfo=datetime.timezone.utc)),
]


# Country codes dos placeholder teams usados em todos os jogos do
# mata-mata. Devem existir apos executar o seeder de teams
# (ver teams.py - bloco "Placeholders TBD").
TBD_HOME_COUNTRY_CODE = 'TBD-H'
TBD_AWAY_COUNTRY_CODE = 'TBD-A'


def upsert_knockout_matches():
    """Insere ou atualiza os 32 jogos do mata-mata.

    A busca idempotente e feita pela tripla
    (round, stadium, match_datetime) - essa combinacao e unica para
    cada jogo do mata-mata (estadio + data/hora + fase) e nao depende
    dos times, que ainda nao estao definidos. Se a partida ja existir,
    atualiza `home_team`, `away_team` e `status` (sem duplicar). Caso
    contrario, cria um novo registro com status='agendado'.

    `home_team` e `away_team` sao preenchidos com os teams placeholder
    (country_code 'TBD-H' e 'TBD-A'). Quando os cruzamentos do mata-mata
    forem conhecidos, basta atualizar esses campos nos registros
    correspondentes. A validacao `home != away` e satisfeita porque
    TBD-H != TBD-A.

    Pre-condicoes: as seeders de teams, stadiums e rounds ja devem ter
    sido executadas (este seeder NAO cria selecoes/estadios/rodadas).

    Returns:
        tuple: (criados, atualizados, total_processados, erros_validacao).
    """
    criados = 0
    atualizados = 0
    erros = 0

    # Cache de lookups para evitar N+1 queries.
    stadiums_by_name = {stadium.name: stadium for stadium in Stadium.objects.all()}
    rounds_by_name = {round_obj.name: round_obj for round_obj in Round.objects.all()}

    # Tenta resolver os placeholders. Se nao existirem, falha explicita
    # (a US-6.6 incluiu esses registros no seeder de teams).
    from matches.models import Team  # import local para evitar ciclo
    try:
        tbd_home = Team.objects.get(country_code=TBD_HOME_COUNTRY_CODE)
    except Team.DoesNotExist:
        raise Team.DoesNotExist(
            f'Team placeholder com country_code "{TBD_HOME_COUNTRY_CODE}" '
            f'nao encontrado. Execute o seeder de teams antes do seeder '
            f'de partidas.',
        )
    try:
        tbd_away = Team.objects.get(country_code=TBD_AWAY_COUNTRY_CODE)
    except Team.DoesNotExist:
        raise Team.DoesNotExist(
            f'Team placeholder com country_code "{TBD_AWAY_COUNTRY_CODE}" '
            f'nao encontrado. Execute o seeder de teams antes do seeder '
            f'de partidas.',
        )

    # Sanity check: placeholders nao podem ser iguais.
    if tbd_home.pk == tbd_away.pk:
        raise ValueError(
            'Placeholders TBD-H e TBD-A devem ser registros distintos.',
        )

    for (
        _match_number,
        round_name,
        stadium_name,
        match_dt,
    ) in WORLD_CUP_2026_KNOCKOUT_MATCHES:
        # `_match_number` (FIFA 73-104) serve apenas para conferencia
        # humana no codigo; nao e persistido no banco.

        round_obj = rounds_by_name.get(round_name)
        stadium = stadiums_by_name.get(stadium_name)

        if round_obj is None or stadium is None:
            erros += 1
            continue

        # Garante datetime aware em UTC.
        if timezone.is_naive(match_dt):
            match_dt = timezone.make_aware(match_dt, datetime.timezone.utc)

        match_obj, created = Match.objects.update_or_create(
            round=round_obj,
            stadium=stadium,
            match_datetime=match_dt,
            defaults={
                'home_team': tbd_home,
                'away_team': tbd_away,
                'status': 'agendado',
            },
        )
        if created:
            criados += 1
        else:
            atualizados += 1

    return criados, atualizados, len(WORLD_CUP_2026_KNOCKOUT_MATCHES), erros
