from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = (
        'Executa todos os seeds em sequencia para popular o banco de dados de desenvolvimento. '
        'Ordem de execucao: seed_users -> seed_pools -> seed_world_cup_2026'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Executa o comando sem pedir confirmacao interativa.',
        )

    def handle(self, *args, **options):
        agora = timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        self.stdout.write(self.style.WARNING(f'=== Seed All iniciado em {agora} ==='))
        self.stdout.write(self.style.WARNING('Ordem de execucao: seed_users -> seed_pools -> seed_world_cup_2026'))
        self.stdout.write('')

        if not options['no_input']:
            resposta = input('Deseja continuar? [y/N]: ')
            if resposta.strip().lower() not in ('y', 'yes'):
                self.stdout.write(self.style.ERROR('Operacao cancelada pelo usuario.'))
                return

        # Step 1: seed_users
        self.stdout.write(self.style.HTTP_INFO('--- Step 1/3: seed_users ---'))
        try:
            call_command('seed_users', no_input=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao executar seed_users: {e}'))
            return

        self.stdout.write('')

        # Step 2: seed_pools
        self.stdout.write(self.style.HTTP_INFO('--- Step 2/3: seed_pools ---'))
        try:
            call_command('seed_pools', no_input=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao executar seed_pools: {e}'))
            return

        self.stdout.write('')

        # Step 3: seed_world_cup_2026
        self.stdout.write(self.style.HTTP_INFO('--- Step 3/3: seed_world_cup_2026 ---'))
        try:
            call_command('seed_world_cup_2026', no_input=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao executar seed_world_cup_2026: {e}'))
            return

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Resumo Final ==='))
        self.stdout.write(self.style.SUCCESS('Todos os seeds foram executados com sucesso!'))
        self.stdout.write('- seed_users: 5 usuarios de teste criados (senha: test1234)')
        self.stdout.write('- seed_pools: 3 boloes de teste com membros')
        self.stdout.write('- seed_world_cup_2026: 48 selecoes, 16 estadio, 7 rodadas, 104 jogos')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'=== Seed All concluido em {timezone.now().strftime("%d/%m/%Y %H:%M:%S")} ==='))
