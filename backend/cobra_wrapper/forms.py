from django import forms
import cobra

from .models import CobraFva


class CleanSbmlContentMixin:
    def clean(self: forms.Form):
        cleaned_data = super().clean()
        try:
            cleaned_data['sbml_content'] = cleaned_data['sbml_content'].read()
        except UnicodeDecodeError:
            self.add_error('sbml_content', 'Can not decode SBML file with utf-8')


class CobraModelCreateForm(CleanSbmlContentMixin, forms.Form):
    sbml_content = forms.FileField()
    name = forms.CharField(max_length=200)


# TODO(myl7)
class CobraModelUpdateForm(CleanSbmlContentMixin, forms.Form):
    sbml_content = forms.FileField()
    objective = forms.CharField(max_length=1000)

    change_type = forms.ChoiceField(choices=[
        ('Use a new sbml file', 'sbml_content'),
        ('Change name', 'name'),
        ('Change objective', 'objective'),
    ])

    def __init__(self, cobra_model: cobra.Model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(max_length=200, initial=cobra_model.name)


# TODO(myl7)
class CobraFvaForm(forms.ModelForm):
    class Meta:
        model = CobraFva
        fields = ['desc', 'reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor']
