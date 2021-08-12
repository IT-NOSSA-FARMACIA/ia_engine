from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.forms import model_to_dict
from django.contrib.auth.decorators import login_required

from .forms import (
    ScheduleForm,
    StepFormSet,
    ScheduleEnvironmentVariableForm,
    ActionForm,
)
from .business import (
    ScheduleBusiness,
    ScheduleEnvironmentVariableBusiness,
    ActionBusiness,
    ScheduleExecutionBusiness,
    TicketBusiness,
)

from .models import (
    Schedule,
    StepSchedule,
    Action,
    ScheduleEnvironmentVariable,
    ScheduleExecution,
    Ticket,
)
from django.conf import settings
from django.contrib import messages


class ScheduleListView(ListView):
    template_name = "schedule/schedule-list.html"
    paginate_by = 5
    model = Schedule
    business_class = ScheduleBusiness
    ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(params=self.request.GET)


class ScheduleView(View):
    business_class = ScheduleBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def post(self, request: HttpRequest, schedule_id: int = 0) -> HttpResponse:
        actions_id = request.POST.getlist("action")
        form = ScheduleForm(request.POST)
        if form.is_valid():
            object_schedule = self.business.update_or_create(
                schedule_id=schedule_id, params=form.cleaned_data, user=request.user
            )
            self.business.update_step_actions(
                schedule=object_schedule, actions_id=actions_id
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("task_engine:schedule", args=(object_schedule.id,)))

    def get(self, request: HttpRequest, schedule_id: int = None) -> HttpResponse:
        if schedule_id:
            schedule = self.business.get(schedule_id=schedule_id)
            form = ScheduleForm(initial=model_to_dict(schedule))
            step_schedule = StepSchedule.objects.filter(schedule=schedule)
            environment_variable = ScheduleEnvironmentVariable.objects.filter(
                schedule=schedule
            )
            extra = {"script": schedule.script}
            extra["step_schedule"] = step_schedule
            extra["environment_variable"] = environment_variable
            formset = {}
        else:
            schedule = None
            extra = {}
            form = ScheduleForm()
            formset = StepFormSet()
        extra["actions"] = Action.objects.filter()
        return render(
            request,
            "schedule/schedule.html",
            {"form": form, "formset": formset, "extra": extra, "schedule": schedule},
        )

    def get_form_kwargs(self):
        """Passes the request object to the form class.
        This is necessary to only display members that belong to a given user"""

        kwargs = super(ScheduleView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class EnvironmentVariableView(View):
    business_class = ScheduleEnvironmentVariableBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def post(self, request, schedule_id):
        form = ScheduleEnvironmentVariableForm(request.POST)
        if form.is_valid():
            self.business.update_or_create(
                schedule_id=schedule_id,
                params=form.cleaned_data,
                pk=request.POST.get("environment_id", 0),
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("task_engine:schedule", args=(schedule_id,)))

    def get(self, request, schedule_id):
        if request.GET.get("method", "").upper() == "DELETE":
            return self.delete(request, schedule_id)
        return HttpResponseNotFound()

    def delete(self, request, schedule_id):
        self.business.delete(environment_id=request.GET.get("environment_id"))
        return redirect(reverse("task_engine:schedule", args=(schedule_id,)))


class ActionListView(ListView):
    template_name = "actions/actions-list.html"
    paginate_by = 5
    model = Action
    business_class = ActionBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(params=self.request.GET)


class ActionView(View):
    business_class = ActionBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def post(self, request: HttpRequest, action_id: int = 0) -> HttpResponse:
        form = ActionForm(request.POST)
        if form.is_valid():
            object_action = self.business.update_or_create(
                action_id=action_id, params=form.cleaned_data, user=request.user
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("task_engine:action", args=(object_action.id,)))

    def get(self, request: HttpRequest, action_id: int = None) -> HttpResponse:
        if action_id:
            action = self.business.get(action_id=action_id)
            form = ActionForm(initial=model_to_dict(action))
            extra = {"script": action.script}
        else:
            action = None
            extra = {}
            form = ActionForm()
        return render(
            request,
            "actions/action.html",
            {"form": form, "action": action, "extra": extra},
        )

    def get_form_kwargs(self):
        """Passes the request object to the form class.
        This is necessary to only display members that belong to a given user"""

        kwargs = super(ActionView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class ScheduleExecutionListView(ListView):
    template_name = "schedule/executions-list.html"
    paginate_by = 20
    model = ScheduleExecution
    business_class = ScheduleExecutionBusiness
    ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(params=self.request.GET)


class ScheduleExecutionView(View):
    business_class = ScheduleExecutionBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get(self, request: HttpRequest, execution_id: int) -> HttpResponse:
        schedule_execution = self.business.get(execution_id=execution_id)
        tickets = self.business.get_tickets(execution_id=execution_id)
        return render(
            request,
            "schedule/execution.html",
            {"schedule_execution": schedule_execution, "tickets": tickets},
        )


class TicketListView(ListView):
    template_name = "ticket/ticket-list.html"
    paginate_by = 20
    model = Ticket
    business_class = TicketBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(params=self.request.GET)


class TicketView(View):
    business_class = TicketBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get(self, request: HttpRequest, ticket_id: int) -> HttpResponse:
        ticket = self.business.get(ticket_id=ticket_id)
        ticket_executions = self.business.get_ticket_executions(
            ticket_id=ticket_id
        ).order_by("-id")
        ticket_parameters = self.business.get_ticket_parameters(
            ticket_id=ticket_id
        ).order_by("name")
        return render(
            request,
            "ticket/ticket.html",
            {
                "ticket": ticket,
                "ticket_executions": ticket_executions,
                "ticket_parameters": ticket_parameters,
            },
        )


class ReprocessTicketView(View):
    business_class = TicketBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def post(self, request: HttpRequest, ticket_id: int) -> HttpResponse:
        ticket = self.business.reprocess_ticket(ticket_id=ticket_id)
        messages.success(request, "Ticket enviado para reprocessamento.")
        return redirect(reverse("task_engine:ticket", args=(ticket.id,)))
