from django import forms
from django.utils import timezone

from .models import Prediction


class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ('home_score', 'away_score')
        widgets = {
            'home_score': forms.NumberInput(attrs={
                'class': (
                    'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
                    'text-white placeholder-gray-500 focus:border-emerald-500 '
                    'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
                    'transition-colors duration-200'
                ),
                'min': 0,
                'placeholder': '0',
            }),
            'away_score': forms.NumberInput(attrs={
                'class': (
                    'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
                    'text-white placeholder-gray-500 focus:border-emerald-500 '
                    'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
                    'transition-colors duration-200'
                ),
                'min': 0,
                'placeholder': '0',
            }),
        }

    def __init__(self, *args, match=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.match = match
        self.fields['home_score'].error_messages = {
            'required': 'Informe o placar do time da casa.',
        }
        self.fields['away_score'].error_messages = {
            'required': 'Informe o placar do time visitante.',
        }

    def clean(self):
        cleaned_data = super().clean()
        if self.match is not None and self.match.match_datetime <= timezone.now():
            raise forms.ValidationError(
                'Palpite indisponível - jogo já começou.',
            )
        return cleaned_data
