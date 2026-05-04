"""Forms used to create and configure MagicBook projects."""

from django import forms
from .models import Project, BRAND_VOICE_CHOICES, AI_MODEL_CHOICES, MARKET_CHOICES


class ProjectCreateForm(forms.ModelForm):
    """Entry form for a new project with niche, tone, model and markets."""

    niche_input = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': (
                'Ej: "Quiero vender un curso de cocina vegana para madres ocupadas" '
                'o "E-book sobre finanzas personales para jóvenes de 20-30 años"'
            ),
            'class': 'w-full bg-gray-800 border border-gray-600 text-gray-100 rounded-lg '
                     'p-4 text-base focus:outline-none focus:border-violet-500 '
                     'focus:ring-1 focus:ring-violet-500 resize-none placeholder-gray-500',
        }),
        label='¿Cuál es tu nicho o idea de infoproducto?',
    )

    brand_voice = forms.ChoiceField(
        choices=BRAND_VOICE_CHOICES,
        initial='mentor',
        widget=forms.RadioSelect,
        label='Voz de Marca',
    )

    ai_model = forms.ChoiceField(
        choices=AI_MODEL_CHOICES,
        initial='gpt-4o',
        widget=forms.RadioSelect,
        label='Modelo de IA',
    )

    primary_market = forms.ChoiceField(
        choices=MARKET_CHOICES,
        initial='LATAM',
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-violet-500'
        }),
        label='Mercado principal',
    )

    target_markets = forms.MultipleChoiceField(
        choices=MARKET_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Mercados objetivo (multi-mercado)',
    )

    def clean_target_markets(self):
        """Guarantee that the primary market is always part of target markets."""
        markets = self.cleaned_data.get('target_markets') or []
        primary = self.cleaned_data.get('primary_market')
        if primary and primary not in markets:
            markets.append(primary)
        return markets

    class Meta:
        model  = Project
        fields = ['niche_input', 'brand_voice', 'ai_model', 'primary_market', 'target_markets']
