from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import formset_factory

from core.models import Team
from .models import Action, Schedule


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class StepForm(forms.Form):
    team = forms.ModelChoiceField(
        queryset=Action.objects.all().order_by(
            "name"
        ),  # .filter(user=self.request.user))
        # label=_("Time"), # aplica translate
        label="Ação",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )


StepFormSet = formset_factory(StepForm, extra=10)


class ScheduleForm(forms.Form):
    name = forms.CharField(label="Nome", required=False, widget=forms.TextInput())
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    script = forms.CharField(
        label="Code",
        required=False,
        widget=forms.Textarea(attrs={"rows": 10, "class": "python-editor"}),
    )
    days = forms.CharField(
        label="Dias",
        required=False,
        widget=forms.TextInput(),
    )
    hours = forms.CharField(
        label="Horas",
        required=False,
        widget=forms.TextInput(),
    )
    minutes = forms.CharField(
        label="Minutos",
        required=False,
        widget=forms.TextInput(),
    )
    cron = forms.CharField(
        label="Cron",
        required=False,
        widget=forms.TextInput(attrs={"v-on:input": "cronTranslate"}),
    )
    last_execution = forms.DateTimeField(
        label="Última Execução",
        required=False,
        # widget=DateTimeInput(),
    )
    last_value = forms.CharField(
        label="Valor de Controle",
        required=False,
        widget=forms.TextInput(),
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
    action = forms.ModelChoiceField(
        queryset=Action.objects.all().order_by(
            "name"
        ),  # .filter(user=self.request.user))
        # label=_("Time"), # aplica translate
        label="Step Action",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    active = forms.BooleanField(
        label="&nbsp Ativo",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Schedule
        fields = ("script__code",)

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


class ScheduleEnvironmentVariableForm(forms.Form):
    name = forms.CharField(label="Nome", required=True, widget=forms.TextInput())
    value = forms.CharField(
        label="Descrição",
        required=True,
        widget=forms.TextInput(),
    )


class ActionForm(forms.Form):
    name = forms.CharField(label="Nome", required=False, widget=forms.TextInput())
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    script = forms.CharField(
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

    class Meta:
        model = Schedule
        fields = ("script__code",)
