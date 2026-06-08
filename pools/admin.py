from django.contrib import admin

from .models import Pool, PoolMember


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'invite_token', 'created_at')


@admin.register(PoolMember)
class PoolMemberAdmin(admin.ModelAdmin):
    list_display = ('pool', 'user', 'joined_at')