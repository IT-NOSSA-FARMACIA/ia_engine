from task_engine.models import ScheduleExecution, Ticket
from task_engine.choices import (
    EXECUTION_STATUS_SUCCESS,
    EXECUTION_STATUS_ERROR,
    EXECUTION_STATUS_QUEUE,
    EXECUTION_STATUS_PENDING,
    EXECUTION_STATUS_PROCESSING,
)

from datetime import datetime, timedelta
from typing import Dict


def schedule_execution_with_success(time_to_search: int) -> int:
    schedule_execution = ScheduleExecution.objects.filter(
        execution_status=EXECUTION_STATUS_SUCCESS,
        execution_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return schedule_execution


def schedule_execution_total(time_to_search: int) -> int:
    schedule_execution = ScheduleExecution.objects.filter(
        execution_date__gt=datetime.now().date() - timedelta(time_to_search)
    ).count()
    return schedule_execution


def schedule_execution_with_error(time_to_search: int) -> int:
    schedule_execution = ScheduleExecution.objects.filter(
        execution_status=EXECUTION_STATUS_ERROR,
        execution_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return schedule_execution


def schedule_execution_pending(time_to_search: int) -> int:
    schedule_execution = ScheduleExecution.objects.filter(
        execution_status=EXECUTION_STATUS_PENDING,
        execution_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return schedule_execution


def schedule_execution_processing(time_to_search: int) -> int:
    schedule_execution = ScheduleExecution.objects.filter(
        execution_status=EXECUTION_STATUS_PROCESSING,
        execution_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return schedule_execution


def schedule_execution_queue(time_to_search: int) -> int:
    schedule_execution = ScheduleExecution.objects.filter(
        execution_status=EXECUTION_STATUS_QUEUE,
        execution_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return schedule_execution


def ticket_execution_with_success(time_to_search: int) -> int:
    tickets = Ticket.objects.filter(
        execution_status=EXECUTION_STATUS_SUCCESS,
        created_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return tickets


def ticket_execution_total(time_to_search: int) -> int:
    tickets = Ticket.objects.filter(
        created_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return tickets


def ticket_execution_with_error(time_to_search: int) -> int:
    tickets = Ticket.objects.filter(
        execution_status=EXECUTION_STATUS_ERROR,
        created_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return tickets


def ticket_execution_queue(time_to_search: int) -> int:
    tickets = Ticket.objects.filter(
        execution_status=EXECUTION_STATUS_QUEUE,
        created_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return tickets


def ticket_execution_processing(time_to_search: int) -> int:
    tickets = Ticket.objects.filter(
        execution_status=EXECUTION_STATUS_PROCESSING,
        created_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return tickets


def ticket_execution_pending(time_to_search: int) -> int:
    tickets = Ticket.objects.filter(
        execution_status=EXECUTION_STATUS_PENDING,
        created_date__gt=datetime.now().date() - timedelta(time_to_search),
    ).count()
    return tickets


def resume_executions(time_to_search: int) -> Dict[str, int]:
    resume = {}
    resume["total_schedule_execution_success"] = schedule_execution_with_success(
        time_to_search
    )
    resume["total_schedule_execution"] = schedule_execution_total(time_to_search)
    resume["total_schedule_execution_error"] = schedule_execution_with_error(
        time_to_search
    )
    resume["total_schedule_execution_queue"] = schedule_execution_queue(time_to_search)
    resume["total_schedule_execution_processing"] = schedule_execution_processing(
        time_to_search
    )
    resume["total_schedule_execution_pending"] = schedule_execution_pending(
        time_to_search
    )

    resume["total_ticket_execution_success"] = ticket_execution_with_success(
        time_to_search
    )
    resume["total_ticket_execution"] = ticket_execution_total(time_to_search)
    resume["total_ticket_execution_error"] = ticket_execution_with_error(time_to_search)
    resume["total_ticket_execution_queue"] = ticket_execution_queue(time_to_search)
    resume["total_ticket_execution_processing"] = ticket_execution_processing(
        time_to_search
    )
    resume["total_ticket_execution_pending"] = ticket_execution_pending(time_to_search)

    return resume
