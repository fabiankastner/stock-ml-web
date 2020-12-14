from django import forms

class SymbolForm(forms.Form):
    symbol = forms.CharField(label='Enter a Valid Symbol', max_length=4)
