from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import CustomUser


class Command(BaseCommand):
    help = (
        'Popula o banco com usuarios de teste para desenvolvimento e testes. '
        'Senha padrao para todos os usuarios: test1234'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Executa o comando sem pedir confirmacao interativa.',
        )

    def handle(self, *args, **options):
        agora = timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        self.stdout.write(self.style.WARNING(f'=== Seed de Usuarios de Teste iniciado em {agora} ==='))

        if not options['no_input']:
            resposta = input('Deseja continuar? [y/N]: ')
            if resposta.strip().lower() not in ('y', 'yes'):
                self.stdout.write(self.style.ERROR('Operacao cancelada pelo usuario.'))
                return

        test_users = [
            {
                'email': 'user1@test.com',
                'first_name': 'Usuario',
                'last_name': 'Um',
            },
            {
                'email': 'user2@test.com',
                'first_name': 'Usuario',
                'last_name': 'Dois',
            },
            {
                'email': 'user3@test.com',
                'first_name': 'Usuario',
                'last_name': 'Tres',
            },
            {
                'email': 'user4@test.com',
                'first_name': 'Usuario',
                'last_name': 'Quatro',
            },
            {
                'email': 'user5@test.com',
                'first_name': 'Usuario',
                'last_name': 'Cinco',
            },
        ]

        default_password = 'test1234'
        created_count = 0
        existing_count = 0

        for user_data in test_users:
            user, created = CustomUser.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                },
            )
            if created:
                user.set_password(default_password)
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Criado: {user.email}'),
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Ja existe: {user.email}'),
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Resumo ==='))
        self.stdout.write(f'Usuarios criados: {created_count}')
        self.stdout.write(f'Usuarios existentes: {existing_count}')
        self.stdout.write(f'Total: {len(test_users)}')
        self.stdout.write(f'Senha padrao: {default_password}')
