from django.core.management.base import BaseCommand
from django.utils import timezone

from pools.models import Pool, PoolMember
from users.models import CustomUser


class Command(BaseCommand):
    help = (
        'Popula o banco com boloes de teste para desenvolvimento e testes. '
        'Cada bolao tera membros asociados usando usuarios do seed_users.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Executa o comando sem pedir confirmacao interativa.',
        )

    def handle(self, *args, **options):
        agora = timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        self.stdout.write(self.style.WARNING(f'=== Seed de Boloes de Teste iniciado em {agora} ==='))

        if not options['no_input']:
            resposta = input('Deseja continuar? [y/N]: ')
            if resposta.strip().lower() not in ('y', 'yes'):
                self.stdout.write(self.style.ERROR('Operacao cancelada pelo usuario.'))
                return

        # Users that should exist from seed_users
        user_emails = [
            'user1@test.com',
            'user2@test.com',
            'user3@test.com',
            'user4@test.com',
            'user5@test.com',
        ]

        # Fetch users
        users = {}
        for email in user_emails:
            try:
                user = CustomUser.objects.get(email=email)
                users[email] = user
            except CustomUser.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Usuario {email} nao encontrado. Execute seed_users primeiro.'),
                )

        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR('E necessario ter pelo menos 2 usuarios. Execute seed_users primeiro.'),
            )
            return

        test_pools = [
            {
                'name': 'Bolao da Familia',
                'description': 'Competicao entre familiares para a Copa do Mundo 2026. Quem acertar mais palpites ganha o trofeu!',
                'members': [
                    'user1@test.com',
                    'user2@test.com',
                    'user3@test.com',
                ],
                'creator': 'user1@test.com',
            },
            {
                'name': 'Bolao do Trabalho',
                'description': 'Bolhao entre colegas do escritorio. Vamos ver quem entende mais de futebol!',
                'members': [
                    'user1@test.com',
                    'user4@test.com',
                    'user5@test.com',
                ],
                'creator': 'user4@test.com',
            },
            {
                'name': 'Bolao dos Amigos',
                'description': 'Grupo de amigos de longa data. A rivalidade comeca agora!',
                'members': [
                    'user2@test.com',
                    'user3@test.com',
                    'user4@test.com',
                    'user5@test.com',
                ],
                'creator': 'user2@test.com',
            },
        ]

        pools_created = 0
        pools_existing = 0
        members_added = 0
        members_existing = 0

        for pool_data in test_pools:
            pool_name = pool_data['name']
            creator_email = pool_data['creator']

            # Check if creator exists
            if creator_email not in users:
                self.stdout.write(
                    self.style.WARNING(f'Criador {creator_email} nao encontrado. Pulando bolao {pool_name}.'),
                )
                continue

            creator = users[creator_email]

            # Create or get pool (idempotent by name)
            pool, created = Pool.objects.get_or_create(
                name=pool_name,
                defaults={
                    'description': pool_data['description'],
                    'created_by': creator,
                },
            )

            if created:
                pools_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Criado: {pool.name}'),
                )
            else:
                pools_existing += 1
                self.stdout.write(
                    self.style.WARNING(f'Ja existe: {pool.name}'),
                )

            # Add members
            for member_email in pool_data['members']:
                if member_email not in users:
                    self.stdout.write(
                        self.style.WARNING(f'Membro {member_email} nao encontrado. Pulando.'),
                    )
                    continue

                member_user = users[member_email]

                # Check if already member
                member, member_created = PoolMember.objects.get_or_create(
                    pool=pool,
                    user=member_user,
                )

                if member_created:
                    members_added += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  Membro adicionado: {member_user.email}'),
                    )
                else:
                    members_existing += 1
                    self.stdout.write(
                        self.style.WARNING(f'  Ja membro: {member_user.email}'),
                    )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== Resumo ==='))
        self.stdout.write(f'Boloes criados: {pools_created}')
        self.stdout.write(f'Boloes existentes: {pools_existing}')
        self.stdout.write(f'Membros adicionados: {members_added}')
        self.stdout.write(f'Membros existentes: {members_existing}')
        self.stdout.write(f'Total de boloes: {len(test_pools)}')
