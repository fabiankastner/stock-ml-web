from django import forms

class SymbolForm(forms.Form):
    symbol = forms.CharField(label='Your name', max_length=4)
