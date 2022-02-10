from django import forms
from .models import Input, Job

class InputForm(forms.ModelForm):
    """Formular for InputFinder Model
    """
    class Meta:
        model = Input
        fields = ['sequence']


class PickBlastRef(forms.Form):
    pick = forms.BooleanField(label='Pick')


class JobForm(forms.ModelForm):
    
    class Meta:
        model  = Job
        fields = ['key']


class JobKeyForm(forms.Form):
    key = forms.CharField(max_length=6)
