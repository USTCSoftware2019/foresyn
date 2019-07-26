from django import forms


class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=127)

    search_by = forms.CharField(max_length=127)
