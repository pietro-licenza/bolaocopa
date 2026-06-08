from django.contrib import admin

from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'pool', 'home_score', 'away_score', 'points')
    list_filter = ('pool',)
    search_fields = ('user__email',)
