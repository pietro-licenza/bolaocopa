"""Seeder das 48 selecoes classificadas para a Copa do Mundo FIFA 2026.

Lista oficial de selecoes que disputarao a Copa do Mundo 2026, incluindo
sedes (Canada, EUA, Mexico) e classificadas via eliminatorias das seis
confederacoes da FIFA, finalizadas em 31 de marco de 2026.

Cada entrada contem:
- name: nome oficial em portugues.
- country_code: codigo FIFA de 3 letras.
- confederation: confederacao da FIFA.
- flag_emoji: emoji da bandeira nacional.
"""

from matches.models import Team


# Lista ordenada por confederacao, depois por nome.
WORLD_CUP_2026_TEAMS = [
    # CONCACAF - Hosts
    ('Canada', 'CAN', Team.Confederation.CONCACAF, '\U0001F1E8\U0001F1E6'),
    ('Mexico', 'MEX', Team.Confederation.CONCACAF, '\U0001F1F2\U0001F1FD'),
    ('Estados Unidos', 'USA', Team.Confederation.CONCACAF, '\U0001F1FA\U0001F1F8'),
    # CONCACAF - Classificadas
    ('Curacao', 'CUW', Team.Confederation.CONCACAF, '\U0001F1E8\U0001F1FC'),
    ('Haiti', 'HAI', Team.Confederation.CONCACAF, '\U0001F1ED\U0001F1F9'),
    ('Panama', 'PAN', Team.Confederation.CONCACAF, '\U0001F1F5\U0001F1E6'),
    # CONCACAF - Playoff intercontinental
    ('Republica Democratica do Congo', 'COD', Team.Confederation.CAF, '\U0001F1E8\U0001F1E9'),
    # CONMEBOL
    ('Argentina', 'ARG', Team.Confederation.CONMEBOL, '\U0001F1E6\U0001F1F7'),
    ('Brasil', 'BRA', Team.Confederation.CONMEBOL, '\U0001F1E7\U0001F1F7'),
    ('Colombia', 'COL', Team.Confederation.CONMEBOL, '\U0001F1E8\U0001F1F4'),
    ('Equador', 'ECU', Team.Confederation.CONMEBOL, '\U0001F1EA\U0001F1E8'),
    ('Paraguai', 'PAR', Team.Confederation.CONMEBOL, '\U0001F1F5\U0001F1FE'),
    ('Uruguai', 'URU', Team.Confederation.CONMEBOL, '\U0001F1FA\U0001F1FE'),
    # UEFA
    ('Alemanha', 'GER', Team.Confederation.UEFA, '\U0001F1E9\U0001F1EA'),
    ('Austria', 'AUT', Team.Confederation.UEFA, '\U0001F1E6\U0001F1F9'),
    ('Belgica', 'BEL', Team.Confederation.UEFA, '\U0001F1E7\U0001F1EA'),
    ('Bosnia e Herzegovina', 'BIH', Team.Confederation.UEFA, '\U0001F1E7\U0001F1E6'),
    ('Chequia', 'CZE', Team.Confederation.UEFA, '\U0001F1E8\U0001F1FF'),
    ('Croatia', 'CRO', Team.Confederation.UEFA, '\U0001F1ED\U0001F1F7'),
    ('Escocia', 'SCO', Team.Confederation.UEFA, '\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F'),
    ('Espanha', 'ESP', Team.Confederation.UEFA, '\U0001F1EA\U0001F1F8'),
    ('Franca', 'FRA', Team.Confederation.UEFA, '\U0001F1EB\U0001F1F7'),
    ('Holanda', 'NED', Team.Confederation.UEFA, '\U0001F1F3\U0001F1F1'),
    ('Inglaterra', 'ENG', Team.Confederation.UEFA, '\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0063\U000E0074\U000E007F'),
    ('Noruega', 'NOR', Team.Confederation.UEFA, '\U0001F1F3\U0001F1F4'),
    ('Portugal', 'POR', Team.Confederation.UEFA, '\U0001F1F5\U0001F1F9'),
    ('Suica', 'SUI', Team.Confederation.UEFA, '\U0001F1E8\U0001F1ED'),
    ('Suecia', 'SWE', Team.Confederation.UEFA, '\U0001F1F8\U0001F1EA'),
    ('Turquia', 'TUR', Team.Confederation.UEFA, '\U0001F1F9\U0001F1F7'),
    # CAF
    ('Africa do Sul', 'RSA', Team.Confederation.CAF, '\U0001F1FF\U0001F1E6'),
    ('Argelia', 'ALG', Team.Confederation.CAF, '\U0001F1E9\U0001F1FF'),
    ('Cabo Verde', 'CPV', Team.Confederation.CAF, '\U0001F1E8\U0001F1FB'),
    ('Costa do Marfim', 'CIV', Team.Confederation.CAF, '\U0001F1E8\U0001F1EE'),
    ('Egito', 'EGY', Team.Confederation.CAF, '\U0001F1EA\U0001F1EC'),
    ('Gana', 'GHA', Team.Confederation.CAF, '\U0001F1EC\U0001F1ED'),
    ('Marracos', 'MAR', Team.Confederation.CAF, '\U0001F1F2\U0001F1E6'),
    ('Senegal', 'SEN', Team.Confederation.CAF, '\U0001F1F8\U0001F1F3'),
    ('Tunisia', 'TUN', Team.Confederation.CAF, '\U0001F1F9\U0001F1F3'),
    # AFC
    ('Arabia Saudita', 'KSA', Team.Confederation.AFC, '\U0001F1F8\U0001F1E6'),
    ('Australia', 'AUS', Team.Confederation.AFC, '\U0001F1E6\U0001F1FA'),
    ('Catar', 'QAT', Team.Confederation.AFC, '\U0001F1F6\U0001F1E6'),
    ('Coreia do Sul', 'KOR', Team.Confederation.AFC, '\U0001F1F0\U0001F1F7'),
    ('Ira', 'IRN', Team.Confederation.AFC, '\U0001F1EE\U0001F1F7'),
    ('Iraque', 'IRQ', Team.Confederation.AFC, '\U0001F1EE\U0001F1F6'),
    ('Japao', 'JPN', Team.Confederation.AFC, '\U0001F1EF\U0001F1F5'),
    ('Jordania', 'JOR', Team.Confederation.AFC, '\U0001F1EF\U0001F1F4'),
    ('Uzbequistao', 'UZB', Team.Confederation.AFC, '\U0001F1FA\U0001F1FF'),
    # OFC
    ('Nova Zelandia', 'NZL', Team.Confederation.OFC, '\U0001F1F3\U0001F1FF'),
    # Placeholders TBD (US-6.6): usados como mandante/visitante nos jogos
    # do mata-mata enquanto os resultados da fase de grupos nao existem.
    # O `country_code` distinto garante `home_team != away_team` (verificado
    # no seeder de mata-mata) e mantem o model `Match` sem `null=True` em
    # home_team/away_team. Quando a fase de grupos for finalizada, basta
    # atualizar os registros para os times reais.
    ('A definir (mandante)', 'TBD-H', '', ''),
    ('A definir (visitante)', 'TBD-A', '', ''),
]


def upsert_teams():
    """Insere ou atualiza as 48 selecoes da Copa 2026.

    A busca e feita pelo country_code. Se a selecao ja existir, atualiza
    name, confederation e flag_emoji (sem duplicar). Caso contrario, cria
    um novo registro.

    Returns:
        tuple: (criados, atualizados, total_processados).
    """
    criados = 0
    atualizados = 0

    for name, country_code, confederation, flag_emoji in WORLD_CUP_2026_TEAMS:
        team, created = Team.objects.update_or_create(
            country_code=country_code,
            defaults={
                'name': name,
                'confederation': confederation,
                'flag_emoji': flag_emoji,
            },
        )
        if created:
            criados += 1
        else:
            atualizados += 1

    return criados, atualizados, len(WORLD_CUP_2026_TEAMS)
