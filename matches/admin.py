from django.contrib import admin

from .models import Match, Round, Stadium, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code', 'confederation', 'flag_emoji')
    list_filter = ('confederation',)
    search_fields = ('name', 'country_code')


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'capacity')
    list_filter = ('country',)
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
        'home_score',
        'away_score',
        'status',
    )
    list_editable = ('home_score', 'away_score', 'status')
    list_filter = ('status', 'round', 'match_datetime')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'match_datetime'
    actions = ['mark_as_finalizado']

    fieldsets = (
        ('Jogo', {
            'fields': ('round', 'stadium', 'home_team', 'away_team', 'match_datetime'),
        }),
        ('Resultado', {
            'fields': ('home_score', 'away_score', 'status'),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    @admin.action(description='Marcar jogos selecionados como finalizado')
    def mark_as_finalizado(self, request, queryset):
        no_score_ids = set(
            queryset.filter(
                home_score__isnull=True,
            ).values_list('pk', flat=True),
        ) | set(
            queryset.filter(
                away_score__isnull=True,
            ).values_list('pk', flat=True),
        )
        if no_score_ids:
            self.message_user(
                request,
                f'{len(no_score_ids)} jogo(s) ignorado(s): placar nao definido.',
                level='warning',
            )
            queryset = queryset.exclude(pk__in=no_score_ids)
        updated = 0
        for match in queryset:
            if match.status != 'finalizado':
                match.status = 'finalizado'
                match.save()
                updated += 1
        self.message_user(
            request,
            f'{updated} jogo(s) marcado(s) como finalizado.',
        )
