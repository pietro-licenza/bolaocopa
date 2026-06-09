from django.contrib import admin

from live.models import MatchEvent


@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_display = ('match', 'minute', 'type', 'player', 'team')
    list_filter = ('type', 'team')
    search_fields = ('player', 'assist_player', 'match__home_team__name',
                     'match__away_team__name')
    autocomplete_fields = ('match', 'team')
