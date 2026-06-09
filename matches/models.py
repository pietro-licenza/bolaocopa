from django.db import models


class Team(models.Model):
    class Confederation(models.TextChoices):
        CONMEBOL = 'CONMEBOL', 'CONMEBOL'
        UEFA = 'UEFA', 'UEFA'
        CAF = 'CAF', 'CAF'
        AFC = 'AFC', 'AFC'
        OFC = 'OFC', 'OFC'
        CONCACAF = 'CONCACAF', 'CONCACAF'

    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=3, unique=True)
    flag_emoji = models.CharField(max_length=10, blank=True)
    confederation = models.CharField(
        max_length=10,
        choices=Confederation.choices,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Stadium(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.city})'


class Round(models.Model):
    PHASE_CHOICES = (
        ('grupo', 'Fase de Grupos'),
        ('trinta_dois_avos', '32-avos de Final'),
        ('oitavas', 'Oitavas de Final'),
        ('quartas', 'Quartas de Final'),
        ('semi', 'Semifinal'),
        ('terceiro_lugar', 'Terceiro Lugar'),
        ('final', 'Final'),
    )

    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return self.name


class Match(models.Model):
    STATUS_CHOICES = (
        ('agendado', 'Agendado'),
        ('em_andamento', 'Em andamento'),
        ('finalizado', 'Finalizado'),
    )

    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name='matches',
    )
    stadium = models.ForeignKey(
        Stadium,
        on_delete=models.PROTECT,
        related_name='matches',
    )
    home_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='home_matches',
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='away_matches',
    )
    match_datetime = models.DateTimeField()
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='agendado',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('match_datetime',)

    def __str__(self):
        return f'{self.home_team} x {self.away_team}'
