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
)

app_name = "task_engine"

urlpatterns = [
    path("schedule/list/", login_required(ScheduleListView.as_view()), name="schedule-list"),
    path("schedule/", login_required(ScheduleView.as_view()), name="schedule"),
    path("schedule/<int:schedule_id>", login_required(ScheduleView.as_view()), name="schedule"),
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
    path("ticket/list/", login_required(TicketListView.as_view()), name="ticket-list"),
    path("ticket/<int:ticket_id>", login_required(TicketView.as_view()), name="ticket"),
    path("ticket/reprocess/<int:ticket_id>", login_required(ReprocessTicketView.as_view()), name="reprocess_ticket"),
]
