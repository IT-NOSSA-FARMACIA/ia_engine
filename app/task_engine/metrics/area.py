from task_engine.models import ScheduleExecution, Ticket
from task_engine.choices import (
    EXECUTION_STATUS_SUCCESS,
    EXECUTION_STATUS_ERROR,
)

from datetime import datetime, timedelta
from typing import Any, Dict
from django.db.models import Count
from core.utils import get_user_team

import datetime as datetime_root


def get_graphics_area_schedule_per_time(time_to_search: int, user) -> Dict[str, Any]:
    convert_sql_date = (
        "CONVERT(VARCHAR(10), execution_date)"
        if time_to_search > 0
        else "CONVERT(VARCHAR(13), execution_date)"
    )

    schedule_execution_success = (
        ScheduleExecution.objects.extra(select={"day": convert_sql_date})
        .values("day")
        .order_by("day")
        .annotate(total=Count("execution_date"))
        .filter(
            execution_status=EXECUTION_STATUS_SUCCESS,
            execution_date__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user),
        )
    )

    schedule_execution_error = (
        ScheduleExecution.objects.extra(select={"day": convert_sql_date})
        .values("day")
        .order_by("day")
        .annotate(total=Count("execution_date"))
        .filter(
            execution_status=EXECUTION_STATUS_ERROR,
            execution_date__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user),
        )
    )

    since = datetime.now().date() - timedelta(time_to_search)
    if time_to_search != 0:
        categories = [
            (since + datetime_root.timedelta(days=idx)).strftime(
                "%Y-%m-%dT00:00:00.000Z"
            )
            for idx in range(time_to_search)
        ]
        categories.append(datetime.now().strftime("%Y-%m-%dT00:00:00.000Z"))
    else:
        today = datetime.now().strftime("%Y-%m-%dT{hour}:00:00.000Z")
        categories = [today.format(hour=str(hour).zfill(2)) for hour in range(24)]

    series_success_data = []
    for category in categories:
        for schedule in schedule_execution_success:
            if schedule["day"].replace(" ", "T") in category:
                series_success_data.append(schedule["total"])
                break
        else:
            series_success_data.append(0)

    series_error_data = []
    for category in categories:
        for schedule in schedule_execution_error:
            if schedule["day"].replace(" ", "T") in category:
                series_error_data.append(schedule["total"])
                break
        else:
            series_error_data.append(0)

    return {
        "series": [
            {"name": "Sucesso", "data": series_success_data},
            {"name": "Erro", "data": series_error_data},
        ],
        "categories": categories,
        "colors": ["#4CED64", "#FF0005"],
    }


def get_graphics_area_ticket_per_time(time_to_search: int, user) -> Dict[str, Any]:
    convert_sql_date = (
        "CONVERT(VARCHAR(10), created_date_ticket)"
        if time_to_search > 0
        else "CONVERT(VARCHAR(13), created_date_ticket)"
    )

    tickets_success = (
        Ticket.objects.extra(select={"day": convert_sql_date})
        .values("day")
        .order_by("day")
        .annotate(total=Count("created_date_ticket"))
        .filter(
            execution_status=EXECUTION_STATUS_SUCCESS,
            created_date_ticket__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user)
        )
    )

    tickets_error = (
        Ticket.objects.extra(select={"day": convert_sql_date})
        .values("day")
        .order_by("day")
        .annotate(total=Count("created_date_ticket"))
        .filter(
            execution_status=EXECUTION_STATUS_ERROR,
            created_date_ticket__gt=datetime.now().date() - timedelta(time_to_search),
            schedule__team__in=get_user_team(user)
        )
    )

    since = datetime.now().date() - timedelta(time_to_search)
    if time_to_search != 0:
        categories = [
            (since + datetime_root.timedelta(days=idx)).strftime(
                "%Y-%m-%dT00:00:00.000Z"
            )
            for idx in range(time_to_search)
        ]
        categories.append(datetime.now().strftime("%Y-%m-%dT00:00:00.000Z"))
    else:
        today = datetime.now().strftime("%Y-%m-%dT{hour}:00:00.000Z")
        categories = [today.format(hour=str(hour).zfill(2)) for hour in range(24)]

    series_success_data = []
    for category in categories:
        for schedule in tickets_success:
            if schedule["day"].replace(" ", "T") in category:
                series_success_data.append(schedule["total"])
                break
        else:
            series_success_data.append(0)

    series_error_data = []
    for category in categories:
        for schedule in tickets_error:
            if schedule["day"].replace(" ", "T") in category:
                series_error_data.append(schedule["total"])
                break
        else:
            series_error_data.append(0)

    return {
        "series": [
            {"name": "Sucesso", "data": series_success_data},
            {"name": "Erro", "data": series_error_data},
        ],
        "categories": categories,
        "colors": ["#4CED64", "#FF0005"],
    }
