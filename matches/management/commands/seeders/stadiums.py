"""Seeder dos 16 estadios sede da Copa do Mundo FIFA 2026.

Lista oficial das 16 cidades-sede confirmadas pela FIFA em 16 de junho
de 2022, com a capacidade maxima publicada pela FIFA para o torneio
(capacidades podem diferir da capacidade nominal do estadio em outros
eventos por conta de configuracoes especificas do mundial).

Cada entrada contem:
- name: nome oficial do estadio.
- city: cidade sede.
- country: pais sede (EUA, Canada ou Mexico).
- capacity: capacidade maxima de publico autorizada pela FIFA.
"""

from matches.models import Stadium


# Lista ordenada por capacidade decrescente.
WORLD_CUP_2026_STADIUMS = [
    # Estados Unidos (11 estadios)
    ('AT&T Stadium', 'Arlington', 'EUA', 94000),
    ('MetLife Stadium', 'East Rutherford', 'EUA', 82500),
    ('Mercedes-Benz Stadium', 'Atlanta', 'EUA', 75000),
    ('Arrowhead Stadium', 'Kansas City', 'EUA', 73000),
    ('NRG Stadium', 'Houston', 'EUA', 72000),
    ("Levi's Stadium", 'Santa Clara', 'EUA', 71000),
    ('SoFi Stadium', 'Inglewood', 'EUA', 70000),
    ('Lincoln Financial Field', 'Philadelphia', 'EUA', 69000),
    ('Lumen Field', 'Seattle', 'EUA', 69000),
    ('Gillette Stadium', 'Foxborough', 'EUA', 65000),
    ('Hard Rock Stadium', 'Miami Gardens', 'EUA', 65000),
    # Canada (2 estadios)
    ('BC Place', 'Vancouver', 'Canada', 54000),
    ('BMO Field', 'Toronto', 'Canada', 45000),
    # Mexico (3 estadios)
    ('Estadio Azteca', 'Mexico City', 'Mexico', 93000),
    ('Estadio BBVA', 'Guadalupe', 'Mexico', 53500),
    ('Estadio Akron', 'Zapopan', 'Mexico', 52000),
]


def upsert_stadiums():
    """Insere ou atualiza os 16 estadios sede da Copa 2026.

    A busca e feita pelo name (nome oficial). Se o estadio ja existir,
    atualiza city, country e capacity (sem duplicar). Caso contrario,
    cria um novo registro.

    Returns:
        tuple: (criados, atualizados, total_processados).
    """
    criados = 0
    atualizados = 0

    for name, city, country, capacity in WORLD_CUP_2026_STADIUMS:
        stadium, created = Stadium.objects.update_or_create(
            name=name,
            defaults={
                'city': city,
                'country': country,
                'capacity': capacity,
            },
        )
        if created:
            criados += 1
        else:
            atualizados += 1

    return criados, atualizados, len(WORLD_CUP_2026_STADIUMS)
