from django.contrib import admin

from .models import Ranking


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('pool', 'user', 'total_points', 'position')
    list_filter = ('pool',)
