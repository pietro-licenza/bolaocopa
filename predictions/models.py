from django.conf import settings
from django.db import models

from matches.models import Match
from pools.models import Pool


class Prediction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions',
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='predictions',
    )
    pool = models.ForeignKey(
        Pool,
        on_delete=models.CASCADE,
        related_name='predictions',
    )
    home_score = models.PositiveIntegerField()
    away_score = models.PositiveIntegerField()
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'match', 'pool')

    def __str__(self):
        return f'{self.user.email} - {self.match} ({self.home_score}x{self.away_score})'
