from django.db import models


class MatchEvent(models.Model):
    """Single in-match event (goal, card, substitution) for a Match.

    Populated from the API-Football ``/fixtures/events`` endpoint during
    :func:`live.services.sync.sync_match_from_api`. The list is cleared
    and rebuilt on every successful sync — the upstream API does not
    expose a stable primary key, so a wipe-and-recreate strategy gives
    the cleanest idempotency guarantee (see US-7.5 / ``TASKS.md``).
    """

    TYPE_CHOICES = (
        ('goal', 'Gol'),
        ('yellow_card', 'Cartao amarelo'),
        ('red_card', 'Cartao vermelho'),
        ('substitution_in', 'Substituicao - entrou'),
        ('substitution_out', 'Substituicao - saiu'),
    )

    match = models.ForeignKey(
        'matches.Match',
        on_delete=models.CASCADE,
        related_name='events',
    )
    minute = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    team = models.ForeignKey(
        'matches.Team',
        on_delete=models.PROTECT,
        related_name='match_events',
    )
    player = models.CharField(max_length=200)
    assist_player = models.CharField(
        max_length=200,
        blank=True,
        default='',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('minute', 'id')
        indexes = [
            # Composite index used to enforce the
            # ``match+minute+type+player`` uniqueness implicit in the
            # API-Football event payloads. Speeds up the wipe-and-
            # recreate sync that drops and re-inserts by match.
            models.Index(
                fields=('match', 'minute', 'type', 'player'),
                name='me_match_min_type_player_idx',
            ),
        ]

    def __str__(self):
        return f'{self.minute}\' {self.get_type_display()} {self.player} ({self.team})'
