from django.urls import path
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
)

app_name = "task_engine"

urlpatterns = [
    path("schedule/list/", ScheduleListView.as_view(), name="schedule-list"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("schedule/<int:schedule_id>", ScheduleView.as_view(), name="schedule"),
    path(
        "environment-variables/<int:schedule_id>",
        EnvironmentVariableView.as_view(),
        name="environment-variable",
    ),
    path("step/", ScheduleView.as_view(), name="step"),
    path("action/list/", ActionListView.as_view(), name="action-list"),
    path("action/", ActionView.as_view(), name="action"),
    path("action/<int:action_id>", ActionView.as_view(), name="action"),
    path(
        "schedule/execution/list/",
        ScheduleExecutionListView.as_view(),
        name="schedule-execution-list",
    ),
    path(
        "schedule/execution/<int:execution_id>",
        ScheduleExecutionView.as_view(),
        name="schedule-execution",
    ),
    path("ticket/list/", TicketListView.as_view(), name="ticket-list"),
    path("ticket/<int:ticket_id>", TicketView.as_view(), name="ticket"),
]
