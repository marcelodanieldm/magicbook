"""Forms for authentication and account onboarding in MagicBook."""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(forms.ModelForm):
    """Registration form with password confirmation and Tailwind-ready widgets."""

    # Password fields are defined explicitly to control UX and validation.
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-800 border border-gray-600 text-gray-100 rounded-lg '
                     'p-3 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500',
            'placeholder': 'Crea una contraseña segura',
        }),
        label='Contraseña',
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-800 border border-gray-600 text-gray-100 rounded-lg '
                     'p-3 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500',
            'placeholder': 'Repite la contraseña',
        }),
        label='Confirmar Contraseña',
    )

    class Meta:
        # Only core identity fields are requested at sign-up time.
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-gray-800 border border-gray-600 text-gray-100 rounded-lg '
                         'p-3 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500',
                'placeholder': 'Nombre de usuario',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-gray-800 border border-gray-600 text-gray-100 rounded-lg '
                         'p-3 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500',
                'placeholder': 'tu@email.com',
            }),
        }

    def clean(self):
        """Ensure both password inputs match before creating the user."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        """Persist user with a hashed password (never plain text)."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
