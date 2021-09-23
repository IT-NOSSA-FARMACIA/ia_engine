from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ScheduleListView,
    ScheduleView,
    EnvironmentVariableView,
    ActionListView,
    ActionView,
    ScheduleExecutionListView,
    ScheduleExecutionView,
    TicketView,
    TicketListView,
    ReprocessTicketView,
    ForceExecutionScheduleView,
    graphics_bar_per_schedule,
    graphics_bar_ticket_per_schedule,
    graphics_area_schedule_per_time,
    graphics_area_ticket_per_time,
)

app_name = "task_engine"

urlpatterns = [
    path(
        "schedule/list/",
        login_required(ScheduleListView.as_view()),
        name="schedule-list",
    ),
    path("schedule/", login_required(ScheduleView.as_view()), name="schedule"),
    path(
        "schedule/<int:schedule_id>",
        login_required(ScheduleView.as_view()),
        name="schedule",
    ),
    path(
        "environment-variables/<int:schedule_id>",
        login_required(EnvironmentVariableView.as_view()),
        name="environment-variable",
    ),
    path("step/", login_required(ScheduleView.as_view()), name="step"),
    path("action/list/", login_required(ActionListView.as_view()), name="action-list"),
    path("action/", login_required(ActionView.as_view()), name="action"),
    path("action/<int:action_id>", login_required(ActionView.as_view()), name="action"),
    path(
        "schedule/execution/list/",
        login_required(ScheduleExecutionListView.as_view()),
        name="schedule-execution-list",
    ),
    path(
        "schedule/execution/<int:execution_id>",
        login_required(ScheduleExecutionView.as_view()),
        name="schedule-execution",
    ),
    path(
        "schedule/graphics_bar/",
        login_required(graphics_bar_per_schedule),
        name="graphics_bar_per_schedule",
    ),
    path(
        "schedule/graphics_area/",
        login_required(graphics_area_schedule_per_time),
        name="graphics_area_schedule_per_time",
    ),
    path(
        "schedule/force_execution/<int:schedule_id>",
        login_required(ForceExecutionScheduleView.as_view()),
        name="schedule-force-execution",
    ),
    path("ticket/list/", login_required(TicketListView.as_view()), name="ticket-list"),
    path("ticket/<int:ticket_id>", login_required(TicketView.as_view()), name="ticket"),
    path(
        "ticket/reprocess/<int:ticket_id>",
        login_required(ReprocessTicketView.as_view()),
        name="reprocess_ticket",
    ),
    path(
        "ticket/graphics_bar/",
        login_required(graphics_bar_ticket_per_schedule),
        name="graphics_bar_ticket_per_schedule",
    ),
    path(
        "ticket/graphics_area/",
        login_required(graphics_area_ticket_per_time),
        name="graphics_area_ticket_per_time",
    ),
]
