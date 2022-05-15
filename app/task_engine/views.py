from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
from django.forms import model_to_dict
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

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
from .metrics.bar import (
    get_graphics_bar_per_schedule,
    get_graphics_bar_ticket_per_schedule,
)

from .metrics.area import (
    get_graphics_area_schedule_per_time,
    get_graphics_area_ticket_per_time,
)
from core.utils import validate_team_user, get_user_team


@method_decorator(permission_required(settings.AUTOMATION_VIEWER), name="get")
class ScheduleListView(ListView):
    template_name = "schedule/schedule-list.html"
    paginate_by = 10
    model = Schedule
    business_class = ScheduleBusiness
    ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(
            params=self.request.GET, user=self.request.user
        )


class ScheduleView(View):
    business_class = ScheduleBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.AUTOMATION_DEVELOPER))
    def post(self, request: HttpRequest, schedule_id: int = 0) -> HttpResponse:
        request_data = request.POST.copy()
        actions_id = request_data.getlist("action")
        if schedule_id:
            schedule = self.business.get(schedule_id=schedule_id, user=request.user)
            request_data.update({"team": schedule.team})
        form = ScheduleForm(request.user, request_data)
        if form.is_valid():
            object_schedule = self.business.update_or_create(
                schedule_id=schedule_id, params=form.cleaned_data, user=request.user
            )
            self.business.update_step_actions(
                schedule=object_schedule, actions_id=actions_id
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("task_engine:schedule", args=(object_schedule.id,)))

    @method_decorator(permission_required(settings.AUTOMATION_VIEWER))
    def get(self, request: HttpRequest, schedule_id: int = None) -> HttpResponse:
        if schedule_id:
            schedule = self.business.get(schedule_id=schedule_id, user=request.user)
            form = ScheduleForm(user=request.user, initial=model_to_dict(schedule))
            step_schedule = StepSchedule.objects.filter(schedule=schedule)
            environment_variable = ScheduleEnvironmentVariable.objects.filter(
                schedule=schedule
            )
            executions = ScheduleExecution.objects.filter(schedule=schedule).order_by(
                "-execution_date"
            )[0:10]
            extra = {"script": schedule.script}
            extra["step_schedule"] = step_schedule
            extra["environment_variable"] = environment_variable
            extra["executions"] = executions
            formset = {}
        else:
            schedule = None
            extra = {}
            form = ScheduleForm(user=request.user)
            formset = StepFormSet()
        if schedule:
            extra["actions"] = Action.objects.filter(team=schedule.team)
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

    @method_decorator(permission_required(settings.AUTOMATION_DEVELOPER))
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

    @method_decorator(permission_required(settings.AUTOMATION_DEVELOPER))
    def get(self, request, schedule_id):
        if request.GET.get("method", "").upper() == "DELETE":
            return self.delete(request, schedule_id)
        return HttpResponseNotFound()

    @method_decorator(permission_required(settings.AUTOMATION_DEVELOPER))
    def delete(self, request, schedule_id):
        self.business.delete(environment_id=request.GET.get("environment_id"))
        return redirect(reverse("task_engine:schedule", args=(schedule_id,)))


@method_decorator(permission_required(settings.AUTOMATION_VIEWER), name="get")
class ActionListView(ListView):
    template_name = "actions/actions-list.html"
    paginate_by = 10
    model = Action
    business_class = ActionBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(
            params=self.request.GET, user=self.request.user
        )


class ActionView(View):
    business_class = ActionBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.AUTOMATION_DEVELOPER))
    def post(self, request: HttpRequest, action_id: int = 0) -> HttpResponse:
        request_data = request.POST.copy()
        if action_id:
            action = self.business.get(action_id=action_id, user=request.user)
            request_data.update({"team": action.team})
        form = ActionForm(request.user, request_data)
        if form.is_valid():
            object_action = self.business.update_or_create(
                action_id=action_id, params=form.cleaned_data, user=request.user
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("task_engine:action", args=(object_action.id,)))

    @method_decorator(permission_required(settings.AUTOMATION_VIEWER))
    def get(self, request: HttpRequest, action_id: int = None) -> HttpResponse:
        if action_id:
            action = self.business.get(action_id=action_id)
            form = ActionForm(initial=model_to_dict(action))
            extra = {"script": action.script}
        else:
            action = None
            extra = {}
            form = ActionForm(user=request.user)
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


@method_decorator(permission_required(settings.AUTOMATION_VIEWER), name="get")
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
        return self.business.get_query_set(
            params=self.request.GET, user=self.request.user
        )


class ScheduleExecutionView(View):
    business_class = ScheduleExecutionBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.AUTOMATION_VIEWER))
    def get(self, request: HttpRequest, execution_id: int) -> HttpResponse:
        schedule_execution = self.business.get(execution_id=execution_id)
        tickets = self.business.get_tickets(execution_id=execution_id)
        return render(
            request,
            "schedule/execution.html",
            {"schedule_execution": schedule_execution, "tickets": tickets},
        )


@method_decorator(permission_required(settings.AUTOMATION_VIEWER), name="get")
class TicketListView(ListView):
    template_name = "ticket/ticket-list.html"
    paginate_by = 20
    model = Ticket
    business_class = TicketBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(
            params=self.request.GET, user=self.request.user
        )


class TicketView(View):
    business_class = TicketBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.AUTOMATION_VIEWER))
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

    @method_decorator(permission_required(settings.AUTOMATION_DEVELOPER))
    def post(self, request: HttpRequest, ticket_id: int) -> HttpResponse:
        ticket = self.business.get(ticket_id=ticket_id)
        self.business.create_task(
            ticket=ticket,
        )
        messages.success(request, "Ticket enviado para reprocessamento.")
        return redirect(reverse("task_engine:ticket", args=(ticket.id,)))


class ForceExecutionScheduleView(View):
    business_class = ScheduleBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.AUTOMATION_DEVELOPER))
    def post(self, request: HttpRequest, schedule_id: int) -> HttpResponse:
        self.business.execute(schedule_id)
        messages.success(
            request,
            "Integração enviada para execução com sucesso. Verifique a execução na lista de execuções.",
        )
        return redirect(reverse("task_engine:schedule", args=(schedule_id,)))


def graphics_bar_per_schedule(request):
    time_to_search = request.GET.get("time", 0)
    if not time_to_search:
        time_to_search = 0
    graphics_bar_data = get_graphics_bar_per_schedule(
        int(time_to_search), user=request.user
    )
    return JsonResponse(graphics_bar_data)


def graphics_bar_ticket_per_schedule(request):
    time_to_search = request.GET.get("time", 0)
    if not time_to_search:
        time_to_search = 0
    graphics_bar_data = get_graphics_bar_ticket_per_schedule(
        int(time_to_search), user=request.user
    )
    return JsonResponse(graphics_bar_data)


def graphics_area_schedule_per_time(request):
    time_to_search = request.GET.get("time", 0)
    if not time_to_search:
        time_to_search = 0
    graphics_bar_data = get_graphics_area_schedule_per_time(
        int(time_to_search), user=request.user
    )
    return JsonResponse(graphics_bar_data)


def graphics_area_ticket_per_time(request):
    time_to_search = request.GET.get("time", 0)
    if not time_to_search:
        time_to_search = 0
    graphics_bar_data = get_graphics_area_ticket_per_time(
        int(time_to_search), user=request.user
    )
    return JsonResponse(graphics_bar_data)
