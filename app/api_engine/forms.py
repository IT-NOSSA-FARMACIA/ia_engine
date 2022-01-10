from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import Team
from .models import (
    FunctionService,
    DomainFunctionService,
    FunctionServiceEnvironmentVariable,
    Customer,
)
from core.utils import get_user_team
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
    public = forms.BooleanField(
        label="&nbsp API Pública",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = FunctionService

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs:
            self.fields["team"].widget.attrs["disabled"] = "true"
        if user:
            self.fields["team"].queryset = Team.objects.filter(user=user).order_by(
                "name"
            )
            self.fields["domain"].queryset = DomainFunctionService.objects.filter(
                team__in=get_user_team(user)
            ).order_by("name")


class FunctionServiceEnvironmentVariableForm(forms.Form):
    name = forms.CharField(label="Nome", required=True, widget=forms.TextInput())
    value = forms.CharField(
        label="Descrição",
        required=True,
        widget=forms.TextInput(),
    )

    class Meta:
        model = FunctionServiceEnvironmentVariable


class DomainFunctionServiceForm(forms.Form):
    name = forms.CharField(label="Nome", required=True, widget=forms.TextInput())
    url_name = forms.CharField(
        label="Nome URL", required=True, widget=forms.TextInput()
    )
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
        model = DomainFunctionService

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs:
            self.fields["team"].widget.attrs["disabled"] = "true"
        if user:
            self.fields["team"].queryset = Team.objects.filter(user=user).order_by(
                "name"
            )


class CustomerForm(forms.Form):
    name = forms.CharField(label="Nome", required=True, widget=forms.TextInput())
    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by(
            "name"
        ),  # .filter(user=self.request.user))
        # label=_("Time"), # aplica translate
        label="Time",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Customer

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs:
            self.fields["team"].widget.attrs["disabled"] = "true"
        if user:
            self.fields["team"].queryset = Team.objects.filter(user=user).order_by(
                "name"
            )
