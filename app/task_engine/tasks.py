from celery.decorators import task
from datetime import timedelta
from celery.utils.log import get_task_logger
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
    EXECUTION_STATUS_PENDING,
    EXECUTION_STATUS_PROCESSING,
    EXECUTION_STATUS_SUCCESS,
    EXECUTION_STATUS_ERROR,
    EXECUTION_STATUS_QUEUE,
)
from datetime import datetime
from django.utils import timezone
from cron_validator import CronScheduler


logger = get_task_logger(__name__)


@task
def search_new_schedule():
    logger.info("starting task sync_new_calls")
    # validar se faz sentido scria um schedule execution para nao criar execução quando um schedule ainda estiver sendo
    # executado
    for schedule in Schedule.objects.filter(active=True):
        if schedule.cron:
            scheduler = CronScheduler(schedule.cron)
            if scheduler.time_for_execution():
                execute_schedule(schedule.id)
        elif (
            schedule.last_execution is None
            or timezone.now()
            >= schedule.last_execution
            + timedelta(minutes=schedule.minutes)
            + timedelta(days=schedule.days)
            + timedelta(hours=schedule.hours)
            - timedelta(seconds=1)
        ):
            execute_schedule(schedule.id)


@task
def execute_schedule(schedule_id):
    logger.info("starting task sync_new_calls")
    schedule = Schedule.objects.get(id=schedule_id)
    environment_variables = ScheduleEnvironmentVariable.objects.filter(
        schedule=schedule
    )
    parameters = {"ENV": {}}
    for environment_variable in environment_variables:
        parameters["ENV"][environment_variable.name] = environment_variable.load_value
    print(parameters)
    logger.info(schedule.name)
    print(schedule.name)
    status, data_list, execution_log = schedule.script.execute(parameters)
    schedule_execution_status = (
        EXECUTION_STATUS_SUCCESS if status else EXECUTION_STATUS_ERROR
    )
    ScheduleExecution.objects.create(
        schedule=schedule,
        execution_status=schedule_execution_status,
        execution_log=execution_log,
    )
    if (
        isinstance(data_list, list)
        and StepSchedule.objects.filter(schedule=schedule).exists()
    ):
        for data in data_list:
            ticket = Ticket.objects.create(schedule=schedule)
            for key, value in data.items():
                TicketParameter.objects.create(ticket=ticket, name=key, value=value)

    print(data_list)
    print("####")
    print(execution_log)
    schedule.last_execution = timezone.now()
    schedule.save()
    return "aew"


@task
def search_pending_tickets():
    tickets = Ticket.objects.filter(execution_status=EXECUTION_STATUS_PENDING)
    for ticket in tickets:
        ticket.execution_status = EXECUTION_STATUS_QUEUE
        ticket.save()
        print(ticket.execution_status)
        process_ticket(ticket.id)


def process_ticket(ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.status = EXECUTION_STATUS_PROCESSING
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

    steps = StepSchedule.objects.filter(schedule=ticket.schedule).order_by(
        "execution_order"
    )

    for step in steps:
        status, data, execution_log = step.action.script.execute(parameters)
        TicketActionLog.objects.create(
            ticket=ticket, action=step.action, execution_log=execution_log
        )
        if status:
            if isinstance(data, dict):
                for key, value in data.items():
                    parameters[key] = value
                    TicketParameter.objects.create(ticket=ticket, name=key, value=value)
        else:
            if step.stoppable:
                ticket.execution_status = EXECUTION_STATUS_ERROR
                ticket.save()
                break
    else:
        ticket.execution_status = EXECUTION_STATUS_SUCCESS
        ticket.save()
