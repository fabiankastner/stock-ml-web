from django import forms

class SymbolForm(forms.Form):
    symbol = forms.CharField(label='Enter a Valid Symbol', max_length=4)

class LoginForm(forms.Form):
    username = forms.CharField(label='Enter Username')
    password = forms.CharField(label="Enter Password")