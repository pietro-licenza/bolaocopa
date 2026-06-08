from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

    _VALIDATOR_MESSAGES = {
        'The password is too similar to the': 'A senha é muito similar a',
        'This password is too short.': 'A senha deve ter pelo menos 8 caracteres.',
        'This password is too common.': 'Esta senha é muito comum.',
        'This password is entirely numeric.': 'A senha não pode ser totalmente numérica.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        css_class = (
            'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
            'text-white placeholder-gray-500 focus:border-emerald-500 '
            'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
            'transition-colors duration-200'
        )

        self.fields['email'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
        })
        self.fields['first_name'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'Seu nome',
            'autocomplete': 'given-name',
        })
        self.fields['last_name'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'Seu sobrenome',
            'autocomplete': 'family-name',
        })
        self.fields['password1'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'Repita a senha',
            'autocomplete': 'new-password',
        })

        self.fields['email'].error_messages = {
            'required': 'Este campo é obrigatório.',
            'unique': 'Este email já está registrado.',
        }
        self.fields['first_name'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }
        self.fields['last_name'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }
        self.fields['password1'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }

    def _translate_validation_errors(self, errors):
        '''Translate Django password validator error messages to pt-BR.'''
        translated = []
        for error in errors:
            message = str(error.message) if hasattr(error, 'message') else str(error)
            translated_msg = message
            for en_msg, pt_msg in self._VALIDATOR_MESSAGES.items():
                if en_msg in message:
                    translated_msg = pt_msg
                    break
            if translated_msg != message:
                translated.append(
                    ValidationError(translated_msg, code=getattr(error, 'code', ''))
                )
            else:
                translated.append(error)
        return translated

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                'As senhas não coincidem.',
                code='password_mismatch',
            )

        if password2 is not None:
            try:
                validate_password(password2, self.instance)
            except ValidationError as e:
                translated_errors = self._translate_validation_errors(e.error_list)
                raise ValidationError(translated_errors)

        return password2


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Email ou senha incorretos.',
        'inactive': 'Esta conta está desativada.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        css_class = (
            'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
            'text-white placeholder-gray-500 focus:border-emerald-500 '
            'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
            'transition-colors duration-200'
        )

        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
            'type': 'email',
        })
        self.fields['username'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }
        self.fields['password'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'Sua senha',
            'autocomplete': 'current-password',
        })
        self.fields['password'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        css_class = (
            'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
            'text-white placeholder-gray-500 focus:border-emerald-500 '
            'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
            'transition-colors duration-200'
        )

        self.fields['email'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'seu@email.com',
            'autocomplete': 'email',
        })
        self.fields['email'].label = 'Email'
        self.fields['email'].error_messages = {
            'required': 'Este campo é obrigatório.',
        }


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        css_class = (
            'w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 '
            'text-white placeholder-gray-500 focus:border-emerald-500 '
            'focus:ring-1 focus:ring-emerald-500 focus:outline-none '
            'transition-colors duration-200'
        )

        self.fields['new_password1'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password',
        })
        self.fields['new_password1'].label = 'Nova senha'
        self.fields['new_password2'].widget.attrs.update({
            'class': css_class,
            'placeholder': 'Repita a nova senha',
            'autocomplete': 'new-password',
        })
        self.fields['new_password2'].label = 'Confirmar nova senha'