from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Evenement

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = '__all__'  # Include all fields
        labels = {
            'nom': _('Nom de l\'événement'),
            'ville': _('Ville'),
            'pays': _('Pays'),
            'lieu': _('Lieu'),
            'nombres_de_places': _('Nombre de places'),
            'rempli': _('Événement complet'),
            'prix': _('Prix d\'entrée'),
            'entree_gratuit': _('Entrée gratuite'),
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'lieu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres_de_places': forms.NumberInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rempli': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'entree_gratuit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_nombres_de_places(self):
        """Ensure number of places is positive"""
        nombres_de_places = self.cleaned_data.get('nombres_de_places')
        if nombres_de_places is not None and nombres_de_places < 0:
            raise forms.ValidationError(_('Le nombre de places doit être un nombre positif.'))
        return nombres_de_places
