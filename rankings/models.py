from django.conf import settings
from django.db import models

from pools.models import Pool


class Ranking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rankings',
    )
    pool = models.ForeignKey(
        Pool,
        on_delete=models.CASCADE,
        related_name='rankings',
    )
    total_points = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'pool')
        ordering = ('position',)

    def __str__(self):
        return f'{self.user.email} - {self.pool.name} (#{self.position})'
