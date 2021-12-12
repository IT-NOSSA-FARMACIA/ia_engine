from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import formset_factory

from core.models import Team
from .models import Action, Schedule
from .choices import NOTIFICATION_TYPE_CHOICE


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
    name = forms.CharField(label="Nome", required=True, widget=forms.TextInput())
    description = forms.CharField(
        label="Descrição",
        required=True,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    script = forms.CharField(
        label="Code",
        required=False,
        widget=forms.Textarea(attrs={"rows": 10, "class": "python-editor"}),
    )
    days = forms.CharField(
        label="Dias",
        required=True,
        initial=0,
        widget=forms.TextInput(),
    )
    hours = forms.CharField(
        label="Horas",
        required=True,
        initial=0,
        widget=forms.TextInput(),
    )
    minutes = forms.CharField(
        label="Minutos",
        required=True,
        initial=0,
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
        required=True,
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
    notification_type = forms.ChoiceField(
        label="Notificar",
        required=True,
        choices=NOTIFICATION_TYPE_CHOICE,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    emails_to_notification = forms.CharField(
        label="Lista de E-mail para Notificação (separados por vírgula)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "data-separator": ",",
                "class": "form-control tagin",
                "data-placeholder": "Adicione o e-mail, depois pressione virgula",
            }
        ),
    )

    class Meta:
        model = Schedule
        fields = ("script__code",)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs:
            self.fields["team"].widget.attrs["disabled"] = "true"
        if user:
            self.fields["team"].queryset = Team.objects.filter(user=user).order_by(
                "name"
            )


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

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs:
            self.fields["team"].widget.attrs["disabled"] = "true"
        if user:
            self.fields["team"].queryset = Team.objects.filter(user=user).order_by(
                "name"
            )
