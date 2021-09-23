from task_engine.models import Schedule, ScheduleExecution, Ticket
from task_engine.choices import (
    EXECUTION_STATUS_SUCCESS,
    EXECUTION_STATUS_ERROR,
)

from datetime import datetime, timedelta
from typing import Any, Dict
from django.db.models import Count
from core.utils import get_user_team


def get_graphics_bar_per_schedule(time_to_search: int, user) -> Dict[str, Any]:
    schedule_error = (
        ScheduleExecution.objects.values("schedule__name")
        .filter(
            execution_status=EXECUTION_STATUS_ERROR,
            execution_date__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user),
        )
        .annotate(total=Count("schedule__name"))
    )
    new_schedule_error = {}
    for schedule in schedule_error:
        new_schedule_error[schedule.get("schedule__name")] = schedule.get("total")

    schedule_success = (
        ScheduleExecution.objects.values("schedule__name")
        .filter(
            execution_status=EXECUTION_STATUS_SUCCESS,
            execution_date__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user),
        )
        .annotate(total=Count("schedule__name"))
    )
    new_schedule_success = {}
    for schedule in schedule_success:
        new_schedule_success[schedule.get("schedule__name")] = schedule.get("total")

    all_schedule = Schedule.objects.filter(team__in=get_user_team(user))

    categories = []
    total_success = []
    total_error = []
    for schedule in all_schedule:
        if new_schedule_success.get(schedule.name) or new_schedule_error.get(
            schedule.name
        ):
            categories.append(schedule.name)
            total_success.append(new_schedule_success.get(schedule.name, 0))
            total_error.append(new_schedule_error.get(schedule.name, 0))

    series_bar = [
        {"name": "Sucesso", "data": total_success},
        {"name": "Erro", "data": total_error},
    ]
    return {
        "series": series_bar,
        "categories": categories,
        "colors": ["#4CED64", "#FF0005"],
    }


def get_graphics_bar_ticket_per_schedule(time_to_search: int, user) -> Dict[str, Any]:
    ticket_error = (
        Ticket.objects.values("schedule__name")
        .filter(
            execution_status=EXECUTION_STATUS_ERROR,
            created_date_ticket__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user),
        )
        .annotate(total=Count("schedule__name"))
    )
    new_ticket_error = {}
    for ticket in ticket_error:
        new_ticket_error[ticket.get("schedule__name")] = ticket.get("total")

    ticket_success = (
        Ticket.objects.values("schedule__name")
        .filter(
            execution_status=EXECUTION_STATUS_SUCCESS,
            created_date_ticket__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user),
        )
        .annotate(total=Count("schedule__name"))
    )
    new_ticket_success = {}
    for ticket in ticket_success:
        new_ticket_success[ticket.get("schedule__name")] = ticket.get("total")

    all_schedule = Schedule.objects.filter(team__in=get_user_team(user))

    categories = []
    total_success = []
    total_error = []
    for schedule in all_schedule:
        if new_ticket_success.get(schedule.name) or new_ticket_error.get(schedule.name):
            categories.append(schedule.name)
            total_success.append(new_ticket_success.get(schedule.name, 0))
            total_error.append(new_ticket_error.get(schedule.name, 0))

    series_bar = [
        {"name": "Sucesso", "data": total_success},
        {"name": "Erro", "data": total_error},
    ]
    return {
        "series": series_bar,
        "categories": categories,
        "colors": ["#4CED64", "#FF0005"],
    }
