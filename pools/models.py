import uuid

from django.conf import settings
from django.db import models


class Pool(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    invite_token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_pools',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PoolMember(models.Model):
    pool = models.ForeignKey(
        Pool,
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pool_memberships',
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pool', 'user')

    def __str__(self):
        return f'{self.user.email} - {self.pool.name}'