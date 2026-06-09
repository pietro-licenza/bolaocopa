"""Seeder das fases/rodadas da Copa do Mundo FIFA 2026.

Formato oficial (aprovado pelo FIFA Council em 14 de marco de 2023):
48 selecoes divididas em 12 grupos de 4. Classificam-se os 2 primeiros
de cada grupo + os 8 melhores terceiros (32 times) para o mata-mata,
disputado em 6 fases ate a final em 19 de julho de 2026.

Calendario oficial:
- Fase de Grupos: 11 a 27 de junho de 2026
- 16-avos de Final: 28 de junho a 3 de julho de 2026
- Oitavas de Final: 4 a 7 de julho de 2026
- Quartas de Final: 9 a 11 de julho de 2026
- Semifinais: 14 e 15 de julho de 2026
- Disputa de 3o lugar: 18 de julho de 2026
- Final: 19 de julho de 2026 (MetLife Stadium, East Rutherford)

Observacao: o codigo ``phase`` (choices do model) continua sendo
``trinta_dois_avos`` por estabilidade retroativa -- apenas o rotulo
visivel ("16-avos de Final") foi atualizado para refletir a nomenclatura
oficial da FIFA. A data migration ``0008_round_rename_32avos_to_16avos``
sincroniza o ``name`` dos registros existentes.

Cada entrada contem:
- name: nome oficial em portugues.
- order: ordem cronologica da fase (usada para ordenacao).
- phase: codigo da fase (choices do model Round).
- start_date: data de inicio dos jogos da fase.
- end_date: data do ultimo jogo da fase.
"""

import datetime

from matches.models import Round


# Lista ordenada por ordem cronologica do torneio.
WORLD_CUP_2026_ROUNDS = [
    (
        'Fase de Grupos',
        1,
        'grupo',
        datetime.date(2026, 6, 11),
        datetime.date(2026, 6, 27),
    ),
    (
        '16-avos de Final',
        2,
        'trinta_dois_avos',
        datetime.date(2026, 6, 28),
        datetime.date(2026, 7, 3),
    ),
    (
        'Oitavas de Final',
        3,
        'oitavas',
        datetime.date(2026, 7, 4),
        datetime.date(2026, 7, 7),
    ),
    (
        'Quartas de Final',
        4,
        'quartas',
        datetime.date(2026, 7, 9),
        datetime.date(2026, 7, 11),
    ),
    (
        'Semifinal',
        5,
        'semi',
        datetime.date(2026, 7, 14),
        datetime.date(2026, 7, 15),
    ),
    (
        'Disputa de 3o Lugar',
        6,
        'terceiro_lugar',
        datetime.date(2026, 7, 18),
        datetime.date(2026, 7, 18),
    ),
    (
        'Final',
        7,
        'final',
        datetime.date(2026, 7, 19),
        datetime.date(2026, 7, 19),
    ),
]


def upsert_rounds():
    """Insere ou atualiza as 7 fases da Copa 2026.

    A busca e feita pelo name (nome oficial). Se a rodada ja existir,
    atualiza order, phase, start_date e end_date (sem duplicar). Caso
    contrario, cria um novo registro.

    Returns:
        tuple: (criados, atualizados, total_processados).
    """
    criados = 0
    atualizados = 0

    for name, order, phase, start_date, end_date in WORLD_CUP_2026_ROUNDS:
        round_obj, created = Round.objects.update_or_create(
            name=name,
            defaults={
                'order': order,
                'phase': phase,
                'start_date': start_date,
                'end_date': end_date,
            },
        )
        if created:
            criados += 1
        else:
            atualizados += 1

    return criados, atualizados, len(WORLD_CUP_2026_ROUNDS)
