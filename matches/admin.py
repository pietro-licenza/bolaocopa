from django.contrib import admin

from .models import Match, Round, Stadium, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code', 'flag_emoji')


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country')
    search_fields = ('name', 'city', 'country')


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'phase')
    list_filter = ('phase',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'home_team',
        'away_team',
        'match_datetime',
        'stadium',
        'status',
    )
    list_filter = ('status', 'round')
    search_fields = ('home_team__name', 'away_team__name')
