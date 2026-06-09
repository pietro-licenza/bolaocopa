"""Renomeia a fase de 32-avos para 16-avos de Final.

O ``Round.name`` usado pelo seeder e exibido no chaveamento
(``templates/matches/match_bracket.html``) era "32-avos de Final" ate
a renomeacao oficial para "16-avos de Final" solicitada na US-X.X.
Como o seeder ``matches.management.commands.seeders.rounds`` faz
``update_or_create(name=name, ...)``, renomear o ``name`` no seeder
sem migrar os dados existentes duplicaria a fase (criaria um novo
registro com o novo nome e manteria o antigo orfao).

Esta data migration atualiza o ``name`` do registro existente para o
novo rotulo, em sincronia com o seeder. O codigo ``phase``
(``trinta_dois_avos``) NAO e alterado: ele continua sendo a chave
estavel usada em queries e signals -- apenas o rotulo visivel ao
usuario muda, o que e feito em um ``AlterField`` na mesma migration.
"""
from django.db import migrations, models


def rename_round_to_16avos(apps, schema_editor):
    """Renomeia ``Round.name`` de "32-avos de Final" para "16-avos de Final"."""
    Round = apps.get_model('matches', 'Round')
    Round.objects.filter(name='32-avos de Final').update(name='16-avos de Final')


def reverse_rename_round(apps, schema_editor):
    """Reversao: volta o ``name`` para "32-avos de Final"."""
    Round = apps.get_model('matches', 'Round')
    Round.objects.filter(name='16-avos de Final').update(name='32-avos de Final')


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0007_match_elapsed_minute'),
    ]

    operations = [
        # 1) Atualiza o rotulo visivel nas choices (usado por
        #    ``Round.get_phase_display()``). O codigo (``trinta_dois_avos``)
        #    permanece estavel para nao quebrar dados existentes.
        migrations.AlterField(
            model_name='round',
            name='phase',
            field=models.CharField(
                choices=[
                    ('grupo', 'Fase de Grupos'),
                    ('trinta_dois_avos', '16-avos de Final'),
                    ('oitavas', 'Oitavas de Final'),
                    ('quartas', 'Quartas de Final'),
                    ('semi', 'Semifinal'),
                    ('terceiro_lugar', 'Terceiro Lugar'),
                    ('final', 'Final'),
                ],
                max_length=20,
            ),
        ),
        # 2) Atualiza o ``name`` do registro existente para o novo
        #    rotulo, em sincronia com o seedor.
        migrations.RunPython(rename_round_to_16avos, reverse_rename_round),
    ]
