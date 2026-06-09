"""Seeder dos 72 jogos da fase de grupos da Copa do Mundo FIFA 2026.

Lista completa dos 72 jogos da fase de grupos, com data, hora (UTC) e
estadio, conforme o calendario oficial divulgado pela FIFA.

Fontes consultadas (via webfetch):
- Sorteio oficial: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_draw
  (sorteio realizado em 5 de dezembro de 2025, no Kennedy Center em
  Washington, D.C.). Define a composicao dos 12 grupos (A a L).
- Calendario oficial: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup
  (revisao de junho de 2026, secao "Group stage" com todos os 72 jogos,
  datas, horarios UTC e estadios). O calendario original foi divulgado
  pela FIFA em 4 de fevereiro de 2024 e atualizado depois.

Formato da Copa 2026:
- 12 grupos (A-L) de 4 selecoes cada.
- 6 jogos por grupo em formato de rodizio (todos contra todos), totalizando
  72 jogos na fase de grupos.
- Jogos realizados entre 11 e 27 de junho de 2026.

Agrupamento no model Round:
- O model `Round` representa uma FASE do torneio (campo `phase` em
  choices: grupo, oitavas, quartas...). O seeder da US-6.4 ja criou
  uma unica Round chamada "Fase de Grupos" (order=1, phase='grupo')
  cobrindo a janela 11-27/jun. Por isso todos os 72 jogos sao
  associados a essa mesma Round, mantendo a semantica de fase
  (e nao de grupo individual). Caso futuro se deseje listar
  "Grupo A", "Grupo B" etc., isso deve ser modelado em uma entidade
  separada (ex: Group) - nao em Round.

Cada entrada da lista e uma tupla com:
- home_team: codigo FIFA de 3 letras (ex: 'BRA').
- away_team: codigo FIFA de 3 letras.
- stadium:  nome oficial do estadio (deve existir em matches.models.Stadium).
- utc_datetime: datetime aware em UTC do kick-off.

Os horarios foram convertidos para UTC a partir do offset local
publicado pela FIFA (UTC-3 a UTC-7), garantindo que `match_datetime`
armazene o instante absoluto do jogo independente do fuso do projeto.
"""

import datetime

from django.utils import timezone

from matches.models import Match, Round, Stadium, Team


# Lista ordenada por data/hora do kick-off (UTC).
# Origem primaria: calendario oficial FIFA (fev/2024, atualizado) e sorteio
# oficial de 5/dez/2025. Conferido com o artigo "2026 FIFA World Cup" da
# Wikipedia en (revisao de junho de 2026, secao "Group stage").
WORLD_CUP_2026_GROUP_MATCHES = [
    # ===== Match 1 - 11/06/2026 =====
    ('MEX', 'RSA', 'Estadio Azteca',
     datetime.datetime(2026, 6, 11, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 2 - 11/06/2026 =====
    ('KOR', 'CZE', 'Estadio Akron',
     datetime.datetime(2026, 6, 12, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 3 - 12/06/2026 =====
    ('CAN', 'BIH', 'BMO Field',
     datetime.datetime(2026, 6, 12, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 4 - 12/06/2026 =====
    ('USA', 'PAR', 'SoFi Stadium',
     datetime.datetime(2026, 6, 13, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 5 - 13/06/2026 =====
    ('HAI', 'SCO', 'Gillette Stadium',
     datetime.datetime(2026, 6, 14, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 6 - 13/06/2026 =====
    ('AUS', 'TUR', 'BC Place',
     datetime.datetime(2026, 6, 14, 4, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 7 - 13/06/2026 =====
    ('BRA', 'MAR', 'MetLife Stadium',
     datetime.datetime(2026, 6, 13, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 8 - 13/06/2026 =====
    ('QAT', 'SUI', "Levi's Stadium",
     datetime.datetime(2026, 6, 13, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 9 - 14/06/2026 =====
    ('CIV', 'ECU', 'Lincoln Financial Field',
     datetime.datetime(2026, 6, 14, 23, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 10 - 14/06/2026 =====
    ('GER', 'CUW', 'NRG Stadium',
     datetime.datetime(2026, 6, 14, 17, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 11 - 14/06/2026 =====
    ('NED', 'JPN', 'AT&T Stadium',
     datetime.datetime(2026, 6, 14, 20, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 12 - 14/06/2026 =====
    ('SWE', 'TUN', 'Estadio BBVA',
     datetime.datetime(2026, 6, 15, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 13 - 15/06/2026 =====
    ('KSA', 'URU', 'Hard Rock Stadium',
     datetime.datetime(2026, 6, 15, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 14 - 15/06/2026 =====
    ('ESP', 'CPV', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 6, 15, 16, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 15 - 15/06/2026 =====
    ('IRN', 'NZL', 'SoFi Stadium',
     datetime.datetime(2026, 6, 16, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 16 - 15/06/2026 =====
    ('BEL', 'EGY', 'Lumen Field',
     datetime.datetime(2026, 6, 15, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 17 - 16/06/2026 =====
    ('FRA', 'SEN', 'MetLife Stadium',
     datetime.datetime(2026, 6, 16, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 18 - 16/06/2026 =====
    ('IRQ', 'NOR', 'Gillette Stadium',
     datetime.datetime(2026, 6, 16, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 19 - 16/06/2026 =====
    ('ARG', 'ALG', 'Arrowhead Stadium',
     datetime.datetime(2026, 6, 17, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 20 - 16/06/2026 =====
    ('AUT', 'JOR', "Levi's Stadium",
     datetime.datetime(2026, 6, 17, 4, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 21 - 17/06/2026 =====
    ('GHA', 'PAN', 'BMO Field',
     datetime.datetime(2026, 6, 17, 23, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 22 - 17/06/2026 =====
    ('ENG', 'CRO', 'AT&T Stadium',
     datetime.datetime(2026, 6, 17, 20, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 23 - 17/06/2026 =====
    ('POR', 'COD', 'NRG Stadium',
     datetime.datetime(2026, 6, 17, 17, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 24 - 17/06/2026 =====
    ('UZB', 'COL', 'Estadio Azteca',
     datetime.datetime(2026, 6, 18, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 25 - 18/06/2026 =====
    ('CZE', 'RSA', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 6, 18, 16, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 26 - 18/06/2026 =====
    ('SUI', 'BIH', 'SoFi Stadium',
     datetime.datetime(2026, 6, 18, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 27 - 18/06/2026 =====
    ('CAN', 'QAT', 'BC Place',
     datetime.datetime(2026, 6, 18, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 28 - 18/06/2026 =====
    ('MEX', 'KOR', 'Estadio Akron',
     datetime.datetime(2026, 6, 19, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 29 - 19/06/2026 =====
    ('BRA', 'HAI', 'Lincoln Financial Field',
     datetime.datetime(2026, 6, 20, 0, 30, tzinfo=datetime.timezone.utc)),
    # ===== Match 30 - 19/06/2026 =====
    ('SCO', 'MAR', 'Gillette Stadium',
     datetime.datetime(2026, 6, 19, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 31 - 19/06/2026 =====
    ('TUR', 'PAR', "Levi's Stadium",
     datetime.datetime(2026, 6, 20, 3, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 32 - 19/06/2026 =====
    ('USA', 'AUS', 'Lumen Field',
     datetime.datetime(2026, 6, 19, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 33 - 20/06/2026 =====
    ('GER', 'CIV', 'BMO Field',
     datetime.datetime(2026, 6, 20, 20, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 34 - 20/06/2026 =====
    ('ECU', 'CUW', 'Arrowhead Stadium',
     datetime.datetime(2026, 6, 21, 0, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 35 - 20/06/2026 =====
    ('NED', 'SWE', 'NRG Stadium',
     datetime.datetime(2026, 6, 20, 17, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 36 - 20/06/2026 =====
    ('TUN', 'JPN', 'Estadio BBVA',
     datetime.datetime(2026, 6, 21, 4, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 37 - 21/06/2026 =====
    ('URU', 'CPV', 'Hard Rock Stadium',
     datetime.datetime(2026, 6, 21, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 38 - 21/06/2026 =====
    ('ESP', 'KSA', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 6, 21, 16, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 39 - 21/06/2026 =====
    ('BEL', 'IRN', 'SoFi Stadium',
     datetime.datetime(2026, 6, 21, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 40 - 21/06/2026 =====
    ('NZL', 'EGY', 'BC Place',
     datetime.datetime(2026, 6, 22, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 41 - 22/06/2026 =====
    ('NOR', 'SEN', 'MetLife Stadium',
     datetime.datetime(2026, 6, 23, 0, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 42 - 22/06/2026 =====
    ('FRA', 'IRQ', 'Lincoln Financial Field',
     datetime.datetime(2026, 6, 22, 21, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 43 - 22/06/2026 =====
    ('ARG', 'AUT', 'AT&T Stadium',
     datetime.datetime(2026, 6, 22, 17, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 44 - 22/06/2026 =====
    ('JOR', 'ALG', "Levi's Stadium",
     datetime.datetime(2026, 6, 23, 3, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 45 - 23/06/2026 =====
    ('ENG', 'GHA', 'Gillette Stadium',
     datetime.datetime(2026, 6, 23, 20, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 46 - 23/06/2026 =====
    ('PAN', 'CRO', 'BMO Field',
     datetime.datetime(2026, 6, 23, 23, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 47 - 23/06/2026 =====
    ('POR', 'UZB', 'NRG Stadium',
     datetime.datetime(2026, 6, 23, 17, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 48 - 23/06/2026 =====
    ('COL', 'COD', 'Estadio Akron',
     datetime.datetime(2026, 6, 24, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 49 - 24/06/2026 =====
    ('SCO', 'BRA', 'Hard Rock Stadium',
     datetime.datetime(2026, 6, 24, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 50 - 24/06/2026 =====
    ('MAR', 'HAI', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 6, 24, 22, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 51 - 24/06/2026 =====
    ('SUI', 'CAN', 'BC Place',
     datetime.datetime(2026, 6, 24, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 52 - 24/06/2026 =====
    ('BIH', 'QAT', 'Lumen Field',
     datetime.datetime(2026, 6, 24, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 53 - 24/06/2026 =====
    ('CZE', 'MEX', 'Estadio Azteca',
     datetime.datetime(2026, 6, 25, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 54 - 24/06/2026 =====
    ('RSA', 'KOR', 'Estadio BBVA',
     datetime.datetime(2026, 6, 25, 1, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 55 - 25/06/2026 =====
    ('CUW', 'CIV', 'Lincoln Financial Field',
     datetime.datetime(2026, 6, 25, 20, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 56 - 25/06/2026 =====
    ('ECU', 'GER', 'MetLife Stadium',
     datetime.datetime(2026, 6, 25, 20, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 57 - 25/06/2026 =====
    ('JPN', 'SWE', 'AT&T Stadium',
     datetime.datetime(2026, 6, 25, 23, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 58 - 25/06/2026 =====
    ('TUN', 'NED', 'Arrowhead Stadium',
     datetime.datetime(2026, 6, 25, 23, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 59 - 25/06/2026 =====
    ('TUR', 'USA', 'SoFi Stadium',
     datetime.datetime(2026, 6, 26, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 60 - 25/06/2026 =====
    ('PAR', 'AUS', "Levi's Stadium",
     datetime.datetime(2026, 6, 26, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 61 - 26/06/2026 =====
    ('NOR', 'FRA', 'Gillette Stadium',
     datetime.datetime(2026, 6, 26, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 62 - 26/06/2026 =====
    ('SEN', 'IRQ', 'BMO Field',
     datetime.datetime(2026, 6, 26, 19, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 63 - 26/06/2026 =====
    ('EGY', 'IRN', 'Lumen Field',
     datetime.datetime(2026, 6, 27, 3, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 64 - 26/06/2026 =====
    ('NZL', 'BEL', 'BC Place',
     datetime.datetime(2026, 6, 27, 3, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 65 - 26/06/2026 =====
    ('CPV', 'KSA', 'NRG Stadium',
     datetime.datetime(2026, 6, 27, 0, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 66 - 26/06/2026 =====
    ('URU', 'ESP', 'Estadio Akron',
     datetime.datetime(2026, 6, 27, 0, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 67 - 27/06/2026 =====
    ('PAN', 'ENG', 'MetLife Stadium',
     datetime.datetime(2026, 6, 27, 21, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 68 - 27/06/2026 =====
    ('CRO', 'GHA', 'Lincoln Financial Field',
     datetime.datetime(2026, 6, 27, 21, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 69 - 27/06/2026 =====
    ('ALG', 'AUT', 'Arrowhead Stadium',
     datetime.datetime(2026, 6, 28, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 70 - 27/06/2026 =====
    ('JOR', 'ARG', 'AT&T Stadium',
     datetime.datetime(2026, 6, 28, 2, 0, tzinfo=datetime.timezone.utc)),
    # ===== Match 71 - 27/06/2026 =====
    ('COL', 'POR', 'Hard Rock Stadium',
     datetime.datetime(2026, 6, 27, 23, 30, tzinfo=datetime.timezone.utc)),
    # ===== Match 72 - 27/06/2026 =====
    ('COD', 'UZB', 'Mercedes-Benz Stadium',
     datetime.datetime(2026, 6, 27, 23, 30, tzinfo=datetime.timezone.utc)),
]


def upsert_group_matches():
    """Insere ou atualiza os 72 jogos da fase de grupos.

    A busca idempotente e feita pela tripla
    (home_team, away_team, match_datetime). Se a partida ja existir,
    atualiza round, stadium e status (sem duplicar). Caso contrario,
    cria um novo registro com status='agendado'.

    O `round` e resolvido dinamicamente pela Round 'Fase de Grupos'
    (phase='grupo', order=1), unica para todos os jogos.

    Pre-condicoes: as seeders de teams, stadiums e rounds ja devem ter
    sido executadas (este seeder NAO cria selecoes/estadios/rodadas).

    Returns:
        tuple: (criados, atualizados, total_processados, erros_validacao).
    """
    criados = 0
    atualizados = 0
    erros = 0

    # Cache de lookups para evitar N+1 queries.
    teams_by_code = {team.country_code: team for team in Team.objects.all()}
    stadiums_by_name = {stadium.name: stadium for stadium in Stadium.objects.all()}
    try:
        group_round = Round.objects.get(name='Fase de Grupos')
    except Round.DoesNotExist:
        raise Round.DoesNotExist(
            'Round "Fase de Grupos" nao encontrada. '
            'Execute o seeder de rounds antes do seeder de partidas.',
        )

    for home_code, away_code, stadium_name, match_dt in WORLD_CUP_2026_GROUP_MATCHES:
        # Validacao: home != away.
        if home_code == away_code:
            erros += 1
            continue

        home_team = teams_by_code.get(home_code)
        away_team = teams_by_code.get(away_code)
        stadium = stadiums_by_name.get(stadium_name)

        if home_team is None or away_team is None or stadium is None:
            erros += 1
            continue

        # Garante datetime aware em UTC.
        if timezone.is_naive(match_dt):
            match_dt = timezone.make_aware(match_dt, datetime.timezone.utc)

        match_obj, created = Match.objects.update_or_create(
            home_team=home_team,
            away_team=away_team,
            match_datetime=match_dt,
            defaults={
                'round': group_round,
                'stadium': stadium,
                'status': 'agendado',
            },
        )
        if created:
            criados += 1
        else:
            atualizados += 1

    return criados, atualizados, len(WORLD_CUP_2026_GROUP_MATCHES), erros
