from django.core.management.base import BaseCommand
from django.utils import timezone

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

        self.stdout.write(self.style.SUCCESS('Comando executado (esqueleto).'))
        self.stdout.write(self.style.WARNING('A logica completa de seed sera implementada nas US 6.2 a 6.6.'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Resumo ==='))
        self.stdout.write('Selecoes: 0 (stub - sera implementado na US 6.2)')
        self.stdout.write('Estadios: 0 (stub - sera implementado na US 6.3)')
        self.stdout.write('Rodadas: 0 (stub - sera implementado na US 6.4)')
        self.stdout.write('Jogos: 0 (stub - sera implementado na US 6.5 e 6.6)')
        self.stdout.write(f'Partidas removidas: {total_matches_deletados}')
