from django.utils import timezone
from django.conf import settings

from celery.decorators import task
from celery.utils.log import get_task_logger

from cron_validator import CronScheduler
from datetime import timedelta

from task_engine import business
from task_engine.models import (
    Schedule,
    ScheduleEnvironmentVariable,
    StepSchedule,
    Ticket,
    TicketParameter,
    TicketActionLog,
    ScheduleExecution,
)
from task_engine.choices import (
    EXECUTION_STATUS_PROCESSING,
    EXECUTION_STATUS_SUCCESS,
    EXECUTION_STATUS_ERROR,
    EXECUTION_STATUS_QUEUE,
)
from task_engine.notification import Notification

from typing import List

from .exceptions import ParametersNotFound

logger = get_task_logger(__name__)


@task
def search_new_schedule():
    logger.info("starting task sync_new_calls")
    # validar se faz sentido criae uma validacao se tem um schedule execution a correr
    #  para nao criar execução quando um schedule ainda estiver sendo executado
    for schedule in Schedule.objects.filter(active=True):
        if schedule.cron:
            last_execution_to_compare_cron = (
                schedule.last_execution.strftime("%Y-%m-%d %H:%M")
                if schedule.last_execution
                else None
            )
            scheduler = CronScheduler(schedule.cron)
            cron_execution_time = scheduler.next_execution_time.strftime(
                "%Y-%m-%d %H:%M"
            )
            if (
                scheduler.time_for_execution()
                and cron_execution_time != last_execution_to_compare_cron
            ):
                schedule_business = business.ScheduleBusiness.factory()
                schedule_business.create_task(schedule=schedule)
        elif (
            schedule.last_execution is None
            or timezone.now()
            >= schedule.last_execution
            + timedelta(minutes=schedule.minutes)
            + timedelta(days=schedule.days)
            + timedelta(hours=schedule.hours)
            - timedelta(seconds=1)
        ):
            schedule_business = business.ScheduleBusiness.factory()
            schedule_business.create_task(schedule=schedule)


@task
def execute_schedule(schedule_id, **kwargs):
    logger.info("starting task sync_new_calls")
    schedule = Schedule.objects.get(id=schedule_id)
    environment_variables = ScheduleEnvironmentVariable.objects.filter(
        schedule=schedule
    )
    parameters = kwargs
    parameters["ENV"] = {}
    for environment_variable in environment_variables:
        parameters["ENV"][environment_variable.name] = environment_variable.load_value
    logger.info(schedule.name)
    status, data_list, execution_log, control_value = schedule.script.execute(
        parameters
    )
    schedule_execution_status = (
        EXECUTION_STATUS_SUCCESS if status else EXECUTION_STATUS_ERROR
    )
    schedule_execution = ScheduleExecution.objects.create(
        schedule=schedule,
        execution_status=schedule_execution_status,
        execution_log=execution_log,
    )
    ticket_created = False
    if (
        isinstance(data_list, list)
        and StepSchedule.objects.filter(schedule=schedule).exists()
    ):
        ticket_business = business.TicketBusiness.factory()
        for data in data_list:
            ticket = Ticket.objects.create(
                schedule=schedule, schedule_execution=schedule_execution
            )
            for key, value in data.items():
                TicketParameter.objects.create(ticket=ticket, name=key, value=value)

            ticket_business.create_task(ticket)
            ticket_created = True

    if control_value:
        schedule.last_value = control_value
        schedule.save()

    if (
        settings.EXECUTION_NOTIFICATION_ENABLED
        and (status and not ticket_created)
        or not status
    ):
        notify_execution.delay(schedule_execution_id=schedule_execution.id)


@task
def process_ticket(ticket_id, list_action_order_to_process: List = None):
    if not list_action_order_to_process:
        list_action_order_to_process = []
    ticket_business = business.TicketBusiness.factory()
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.execution_status = EXECUTION_STATUS_PROCESSING
    ticket.save()
    environment_variables = ScheduleEnvironmentVariable.objects.filter(
        schedule=ticket.schedule
    )
    parameters = {"ENV": {}}
    for environment_variable in environment_variables:
        parameters["ENV"][environment_variable.name] = environment_variable.load_value
    ticket_parameters = TicketParameter.objects.filter(ticket=ticket)
    for ticket_parameter in ticket_parameters:
        parameters[ticket_parameter.name] = ticket_parameter.value
    parameters["ticket_id"] = ticket.id

    filter_step_schedule = {"schedule": ticket.schedule}
    if list_action_order_to_process:
        filter_step_schedule["execution_order__in"] = list_action_order_to_process

    steps = StepSchedule.objects.filter(**filter_step_schedule).order_by(
        "execution_order"
    )

    for step in steps:
        status, data, execution_log, _ = step.action.script.execute(parameters)
        TicketActionLog.objects.create(
            ticket=ticket, action=step.action, execution_log=execution_log
        )
        if status:
            if isinstance(data, dict):
                for key, value in data.items():
                    parameters[key] = value
                    TicketParameter.objects.update_or_create(
                        ticket=ticket, name=key, defaults={"value": value}
                    )
                if retry_ticket := data.get("retry_ticket"):
                    list_action_order_to_process = data.get(
                        "step_actions_to_process", []
                    )
                    ticket_business.create_task(
                        ticket=ticket,
                        list_action_order_to_process=list_action_order_to_process,
                        seconds_delay=retry_ticket,
                    )
                    break
        else:
            if step.stoppable:
                ticket.execution_status = EXECUTION_STATUS_ERROR
                ticket.save()
                break
    else:
        ticket.execution_status = EXECUTION_STATUS_SUCCESS
        ticket.save()

    if settings.EXECUTION_NOTIFICATION_ENABLED:
        notify_execution.delay(ticket_id=ticket.id)


@task
def notify_execution(schedule_execution_id: int = None, ticket_id: int = None) -> None:
    ticket = None
    schedule_execution = None
    if ticket_id:
        ticket = Ticket.objects.get(id=ticket_id)
        schedule = ticket.schedule
        execution_status = ticket.execution_status
    elif schedule_execution_id:
        schedule_execution = ScheduleExecution.objects.get(id=schedule_execution_id)
        schedule = schedule_execution.schedule
        execution_status = schedule_execution.execution_status
    else:
        raise ParametersNotFound("schedule_execution_id or ticket_id is mandatory")

    notification = Notification()
    if notification.is_to_notify(schedule.notification_type, execution_status):
        notification.notify(schedule_execution=schedule_execution, ticket=ticket)
