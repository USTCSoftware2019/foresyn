from django import forms


class PasswordConfirmForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
