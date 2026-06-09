from django.core.management.base import BaseCommand
from django.utils import timezone

from matches.management.commands.seeders import rounds as rounds_seeder
from matches.management.commands.seeders import stadiums as stadiums_seeder
from matches.management.commands.seeders import teams as teams_seeder
from matches.models import Match


class Command(BaseCommand):
    help = 'Popula o banco de dados com os dados oficiais da Copa do Mundo FIFA 2026.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Executa o comando sem pedir confirmacao interativa.',
        )

    def handle(self, *args, **options):
        agora = timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        self.stdout.write(self.style.WARNING(f'=== Seed Copa do Mundo 2026 iniciado em {agora} ==='))

        if not options['no_input']:
            resposta = input('Deseja continuar? Este comando apagara todas as partidas existentes. [y/N]: ')
            if resposta.strip().lower() not in ('y', 'yes'):
                self.stdout.write(self.style.ERROR('Operacao cancelada pelo usuario.'))
                return

        total_matches_deletados, _ = Match.objects.all().delete()

        # US-6.2: selecoes (upsert idempotente por country_code).
        teams_criados, teams_atualizados, teams_total = teams_seeder.upsert_teams()
        self.stdout.write(
            self.style.SUCCESS(
                f'Selecoes: {teams_total} processadas ({teams_criados} criadas, {teams_atualizados} atualizadas).',
            ),
        )

        # US-6.3: estadios (upsert idempotente por name).
        stadiums_criados, stadiums_atualizados, stadiums_total = stadiums_seeder.upsert_stadiums()
        self.stdout.write(
            self.style.SUCCESS(
                f'Estadios: {stadiums_total} processados ({stadiums_criados} criados, {stadiums_atualizados} atualizados).',
            ),
        )

        # US-6.4: rodadas/fases (upsert idempotente por name).
        rounds_criados, rounds_atualizados, rounds_total = rounds_seeder.upsert_rounds()
        self.stdout.write(
            self.style.SUCCESS(
                f'Rodadas: {rounds_total} processadas ({rounds_criados} criadas, {rounds_atualizados} atualizadas).',
            ),
        )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Resumo ==='))
        self.stdout.write(f'Selecoes: {teams_total} ({teams_criados} criadas, {teams_atualizados} atualizadas)')
        self.stdout.write(f'Estadios: {stadiums_total} ({stadiums_criados} criados, {stadiums_atualizados} atualizados)')
        self.stdout.write(f'Rodadas: {rounds_total} ({rounds_criados} criadas, {rounds_atualizados} atualizadas)')
        self.stdout.write('Jogos: 0 (stub - sera implementado na US 6.5 e 6.6)')
        self.stdout.write(f'Partidas removidas: {total_matches_deletados}')
