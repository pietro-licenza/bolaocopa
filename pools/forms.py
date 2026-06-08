from django.forms import ModelForm, Textarea, TextInput

from .models import Pool


class PoolForm(ModelForm):
    class Meta:
        model = Pool
        fields = ('name', 'description')
        widgets = {
            'name': TextInput(attrs={
                'class': (
                    'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
                    'text-white placeholder-gray-500 focus:border-emerald-500 '
                    'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
                    'transition-colors duration-200'
                ),
                'placeholder': 'Nome do bolão',
                'maxlength': 100,
            }),
            'description': Textarea(attrs={
                'class': (
                    'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
                    'text-white placeholder-gray-500 focus:border-emerald-500 '
                    'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
                    'transition-colors duration-200'
                ),
                'placeholder': 'Descrição do bolão (opcional)',
                'rows': 4,
                'maxlength': 500,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }

    def clean_description(self):
        value = self.cleaned_data.get('description', '')
        if len(value) > 500:
            self.add_error(
                'description',
                'A descrição deve ter no máximo 500 caracteres.',
            )
        return value