from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import formset_factory

from core.models import Team
from .models import FunctionService, DomainFunctionService
from .choices import HTTP_METHOD_CHOICE

class FunctionServiceForm(forms.Form):
    name = forms.CharField(label="Nome", required=False, widget=forms.TextInput())
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    domain = forms.ModelChoiceField(
        queryset=DomainFunctionService.objects.all().order_by(
            "name"
        ),  # .filter(user=self.request.user))
        # label=_("Time"), # aplica translate
        label="Domínio",
        widget=forms.Select(),
    )
    http_method = forms.ChoiceField(        
        choices=HTTP_METHOD_CHOICE,
        label="Método",
        widget=forms.Select(),
    )
    url_name = forms.CharField(label="Nome URL", widget=forms.TextInput())
    code = forms.CharField(
        label="Code",
        required=False,
        widget=forms.Textarea(attrs={"rows": 10, "class": "python-editor"}),
    )
    # created_date = forms.DateTimeField(
    #     label="Última Execução",
    #     required=False,
    #     # widget=DateTimeInput(),
    # )
    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by(
            "name"
        ),  # .filter(user=self.request.user))
        # label=_("Time"), # aplica translate
        label="Time",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    active = forms.BooleanField(
        label="&nbsp Ativo",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = FunctionService
        #fields = ("code",)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.layout = Layout(
    #         Row(
    #             Column('email', css_class='form-group col-md-6 mb-0'),
    #             Column('password', css_class='form-group col-md-6 mb-0'),
    #             css_class='form-row'
    #         ),
    #         'address_1',
    #         'address_2',
    #         Row(
    #             Column('city', css_class='form-group col-md-6 mb-0'),
    #             Column('state', css_class='form-group col-md-4 mb-0'),
    #             Column('zip_code', css_class='form-group col-md-2 mb-0'),
    #             css_class='form-row'
    #         ),
    #         'check_me_out',
    #         Submit('submit', 'Salvar')
    #     )