"""Seeder das 48 selecoes classificadas para a Copa do Mundo FIFA 2026.

Lista oficial de selecoes que disputarao a Copa do Mundo 2026, incluindo
sedes (Canada, EUA, Mexico) e classificadas via eliminatorias das seis
confederacoes da FIFA, finalizadas em 31 de marco de 2026.

Cada entrada contem:
- name: nome oficial em portugues (exibido na UI).
- name_en: nome oficial em ingles conforme usado pela football-data.org
  (utilizado pelo backfill de ``Match.external_id`` para casar os nomes
  das selecoes com os fixtures da API).
- country_code: codigo FIFA de 3 letras.
- confederation: confederacao da FIFA.
- flag_emoji: emoji da bandeira nacional.
"""

from matches.models import Team


# Lista ordenada por confederacao, depois por nome.
# Os nomes em ingles seguem o spelling oficial da football-data.org
# (consultado em 2026-06-09 via /v4/competitions/2000/teams e /v4/
# competitions/2000/matches). Mudancas da API devem ser refletidas aqui
# para manter o backfill_match_external_ids funcional.
WORLD_CUP_2026_TEAMS = [
    # CONCACAF - Hosts
    ('Canada', 'Canada', 'CAN', Team.Confederation.CONCACAF, '\U0001F1E8\U0001F1E6'),
    ('Mexico', 'Mexico', 'MEX', Team.Confederation.CONCACAF, '\U0001F1F2\U0001F1FD'),
    ('Estados Unidos', 'United States', 'USA', Team.Confederation.CONCACAF, '\U0001F1FA\U0001F1F8'),
    # CONCACAF - Classificadas
    ('Curacao', 'Curaçao', 'CUW', Team.Confederation.CONCACAF, '\U0001F1E8\U0001F1FC'),
    ('Haiti', 'Haiti', 'HAI', Team.Confederation.CONCACAF, '\U0001F1ED\U0001F1F9'),
    ('Panama', 'Panama', 'PAN', Team.Confederation.CONCACAF, '\U0001F1F5\U0001F1E6'),
    # CONCACAF - Playoff intercontinental
    ('Republica Democratica do Congo', 'Congo DR', 'COD', Team.Confederation.CAF, '\U0001F1E8\U0001F1E9'),
    # CONMEBOL
    ('Argentina', 'Argentina', 'ARG', Team.Confederation.CONMEBOL, '\U0001F1E6\U0001F1F7'),
    ('Brasil', 'Brazil', 'BRA', Team.Confederation.CONMEBOL, '\U0001F1E7\U0001F1F7'),
    ('Colombia', 'Colombia', 'COL', Team.Confederation.CONMEBOL, '\U0001F1E8\U0001F1F4'),
    ('Equador', 'Ecuador', 'ECU', Team.Confederation.CONMEBOL, '\U0001F1EA\U0001F1E8'),
    ('Paraguai', 'Paraguay', 'PAR', Team.Confederation.CONMEBOL, '\U0001F1F5\U0001F1FE'),
    ('Uruguai', 'Uruguay', 'URU', Team.Confederation.CONMEBOL, '\U0001F1FA\U0001F1FE'),
    # UEFA
    ('Alemanha', 'Germany', 'GER', Team.Confederation.UEFA, '\U0001F1E9\U0001F1EA'),
    ('Austria', 'Austria', 'AUT', Team.Confederation.UEFA, '\U0001F1E6\U0001F1F9'),
    ('Belgica', 'Belgium', 'BEL', Team.Confederation.UEFA, '\U0001F1E7\U0001F1EA'),
    ('Bosnia e Herzegovina', 'Bosnia-Herzegovina', 'BIH', Team.Confederation.UEFA, '\U0001F1E7\U0001F1E6'),
    ('Chequia', 'Czechia', 'CZE', Team.Confederation.UEFA, '\U0001F1E8\U0001F1FF'),
    ('Croatia', 'Croatia', 'CRO', Team.Confederation.UEFA, '\U0001F1ED\U0001F1F7'),
    ('Escocia', 'Scotland', 'SCO', Team.Confederation.UEFA, '\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F'),
    ('Espanha', 'Spain', 'ESP', Team.Confederation.UEFA, '\U0001F1EA\U0001F1F8'),
    ('Franca', 'France', 'FRA', Team.Confederation.UEFA, '\U0001F1EB\U0001F1F7'),
    ('Holanda', 'Netherlands', 'NED', Team.Confederation.UEFA, '\U0001F1F3\U0001F1F1'),
    ('Inglaterra', 'England', 'ENG', Team.Confederation.UEFA, '\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0063\U000E0074\U000E007F'),
    ('Noruega', 'Norway', 'NOR', Team.Confederation.UEFA, '\U0001F1F3\U0001F1F4'),
    ('Portugal', 'Portugal', 'POR', Team.Confederation.UEFA, '\U0001F1F5\U0001F1F9'),
    ('Suica', 'Switzerland', 'SUI', Team.Confederation.UEFA, '\U0001F1E8\U0001F1ED'),
    ('Suecia', 'Sweden', 'SWE', Team.Confederation.UEFA, '\U0001F1F8\U0001F1EA'),
    ('Turquia', 'Turkey', 'TUR', Team.Confederation.UEFA, '\U0001F1F9\U0001F1F7'),
    # CAF
    ('Africa do Sul', 'South Africa', 'RSA', Team.Confederation.CAF, '\U0001F1FF\U0001F1E6'),
    ('Argelia', 'Algeria', 'ALG', Team.Confederation.CAF, '\U0001F1E9\U0001F1FF'),
    ('Cabo Verde', 'Cape Verde Islands', 'CPV', Team.Confederation.CAF, '\U0001F1E8\U0001F1FB'),
    ('Costa do Marfim', 'Ivory Coast', 'CIV', Team.Confederation.CAF, '\U0001F1E8\U0001F1EE'),
    ('Egito', 'Egypt', 'EGY', Team.Confederation.CAF, '\U0001F1EA\U0001F1EC'),
    ('Gana', 'Ghana', 'GHA', Team.Confederation.CAF, '\U0001F1EC\U0001F1ED'),
    ('Marracos', 'Morocco', 'MAR', Team.Confederation.CAF, '\U0001F1F2\U0001F1E6'),
    ('Senegal', 'Senegal', 'SEN', Team.Confederation.CAF, '\U0001F1F8\U0001F1F3'),
    ('Tunisia', 'Tunisia', 'TUN', Team.Confederation.CAF, '\U0001F1F9\U0001F1F3'),
    # AFC
    ('Arabia Saudita', 'Saudi Arabia', 'KSA', Team.Confederation.AFC, '\U0001F1F8\U0001F1E6'),
    ('Australia', 'Australia', 'AUS', Team.Confederation.AFC, '\U0001F1E6\U0001F1FA'),
    ('Catar', 'Qatar', 'QAT', Team.Confederation.AFC, '\U0001F1F6\U0001F1E6'),
    ('Coreia do Sul', 'South Korea', 'KOR', Team.Confederation.AFC, '\U0001F1F0\U0001F1F7'),
    ('Ira', 'Iran', 'IRN', Team.Confederation.AFC, '\U0001F1EE\U0001F1F7'),
    ('Iraque', 'Iraq', 'IRQ', Team.Confederation.AFC, '\U0001F1EE\U0001F1F6'),
    ('Japao', 'Japan', 'JPN', Team.Confederation.AFC, '\U0001F1EF\U0001F1F5'),
    ('Jordania', 'Jordan', 'JOR', Team.Confederation.AFC, '\U0001F1EF\U0001F1F4'),
    ('Uzbequistao', 'Uzbekistan', 'UZB', Team.Confederation.AFC, '\U0001F1FA\U0001F1FF'),
    # OFC
    ('Nova Zelandia', 'New Zealand', 'NZL', Team.Confederation.OFC, '\U0001F1F3\U0001F1FF'),
    # Placeholders TBD (US-6.6): usados como mandante/visitante nos jogos
    # do mata-mata enquanto os resultados da fase de grupos nao existem.
    # O `country_code` distinto garante `home_team != away_team` (verificado
    # no seeder de mata-mata) e mantem o model `Match` sem `null=True` em
    # home_team/away_team. Quando a fase de grupos for finalizada, basta
    # atualizar os registros para os times reais.
    ('A definir (mandante)', '', 'TBD-H', '', ''),
    ('A definir (visitante)', '', 'TBD-A', '', ''),
]


def upsert_teams():
    """Insere ou atualiza as 48 selecoes da Copa 2026.

    A busca e feita pelo country_code. Se a selecao ja existir, atualiza
    name, name_en, confederation e flag_emoji (sem duplicar). Caso
    contrario, cria um novo registro.

    Returns:
        tuple: (criados, atualizados, total_processados).
    """
    criados = 0
    atualizados = 0

    for name, name_en, country_code, confederation, flag_emoji in WORLD_CUP_2026_TEAMS:
        team, created = Team.objects.update_or_create(
            country_code=country_code,
            defaults={
                'name': name,
                'name_en': name_en,
                'confederation': confederation,
                'flag_emoji': flag_emoji,
            },
        )
        if created:
            criados += 1
        else:
            atualizados += 1

    return criados, atualizados, len(WORLD_CUP_2026_TEAMS)
