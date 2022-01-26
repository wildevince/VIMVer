from django import forms
from .models import InputFinder

class InputFinderForm(forms.ModelForm):
    """Formular for InputFinder Model
    """
    class Meta:
        model = InputFinder
        fields = '__all__'


class PickBlastRef(forms.Form):
    pick = forms.BooleanField(label='Pick')

"""
class sentTo(forms.Form):
    filename = forms.CharField()
"""