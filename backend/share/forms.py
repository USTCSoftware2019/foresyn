from django import forms


class PasswordConfirmForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
