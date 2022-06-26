from copy import deepcopy
from typing import Dict, Type, List

from django.db.models import Model
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone

from task_engine import tasks
from core.utils import validate_team_user, get_user_team

from .choices import EXECUTION_STATUS_QUEUE, EXECUTION_STATUS_QUEUE_RETRY
from .tasks import process_ticket, execute_schedule
from .models import (
    Schedule,
    Script,
    StepSchedule,
    ScheduleEnvironmentVariable,
    Action,
    ScheduleExecution,
    Ticket,
    TicketActionLog,
    TicketParameter,
    TeamWorker,
)

from .exceptions import ObjectNotFound

import pydantic


class ScheduleBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(cls, model_class=Schedule) -> "ScheduleBusiness":
        return cls(model_class=model_class)

    def update_or_create(self, schedule_id: int, params: Dict, user: User) -> Model:
        # Avoid side effects
        params = deepcopy(params)
        script_code = params["script"]
        del params["script"]
        del params["action"]
        params["last_updated_by"] = user
        if schedule_id:
            self.model_class.objects.filter(pk=schedule_id).update(**params)
            object_schedule = self.model_class.objects.get(pk=schedule_id)
            object_schedule.save()  # it is required to enable the historical recording
            script = Script.objects.get(pk=object_schedule.script.pk)
            script.code = script_code
            script.save()
        else:
            script = Script.objects.create(code=script_code)
            params["script"] = script
            params["created_by"] = user
            object_schedule = self.model_class.objects.create(**params)
        return object_schedule

    def execute(self, schedule_id: int):
        schedule = Schedule.objects.get(id=schedule_id)
        team_worker = TeamWorker.objects.filter(team=schedule.team).last()
        if team_worker:
            queue_name = f"execute-schedule-{team_worker.suffix_worker_name}"
        else:
            queue_name = "execute-schedule"
        execute_schedule.apply_async(
            kwargs={"schedule_id": schedule_id}, queue=queue_name
        )

    def update_step_actions(self, schedule: Schedule, actions_id: List):
        StepSchedule.objects.filter(schedule=schedule).delete()
        execution_order = 0
        for action in actions_id:
            if action:
                StepSchedule.objects.create(
                    schedule=schedule, action_id=action, execution_order=execution_order
                )
                execution_order += 1

    def get(self, schedule_id: int = None, user=None) -> Model:
        schedule = self.model_class.objects.get(id=schedule_id)
        if user and not validate_team_user(user, schedule.team):
            raise ObjectNotFound("Schedule Not Found")
        return schedule

    def get_query_set(self, params: Dict, user=None):
        name = params.get("name")
        order_by = params.get("order_by", "id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(name__icontains=name) | Q(description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        if user:
            object_list = object_list.filter(team__in=get_user_team(user))
        return object_list

    def create_task(self, schedule: Schedule):
        team_worker = TeamWorker.objects.filter(team=schedule.team).first()
        if team_worker:
            queue_name = f"execute-schedule-{team_worker.suffix_worker_name}"
        else:
            queue_name = "execute-schedule"

        tasks.execute_schedule.apply_async(
            kwargs={
                "schedule_id": schedule.id,
            },
            queue=queue_name,
        )

        schedule.last_execution = timezone.now()
        schedule.save()


class ScheduleEnvironmentVariableBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(
        cls, model_class=ScheduleEnvironmentVariable
    ) -> "ScheduleEnvironmentVariableBusiness":
        return cls(model_class=model_class)

    def update_or_create(self, schedule_id, params, pk=0):
        params = deepcopy(params)
        if pk:
            environment_variable = self.model_class.objects.get(id=pk)
            environment_variable.name = params["name"]
            environment_variable.value = params["value"]
            environment_variable.save()
            return environment_variable
        else:
            params["schedule"] = Schedule.objects.get(pk=schedule_id)
            print(params)
            # **params
            environment_variable = self.model_class.objects.create(
                name=params["name"], value=params["value"], schedule=params["schedule"]
            )
            return environment_variable

    def delete(self, environment_id):
        print(environment_id)
        self.model_class.objects.get(pk=environment_id).delete()


class ActionBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(cls, model_class=Action) -> "ActionBusiness":
        return cls(model_class=model_class)

    def update_or_create(self, action_id: int, params: Dict, user: User) -> Model:
        # Avoid side effects
        params = deepcopy(params)
        script_code = params["script"]
        del params["script"]
        params["last_updated_by"] = user
        if action_id:
            self.model_class.objects.filter(pk=action_id).update(**params)
            object_action = self.model_class.objects.get(pk=action_id)
            object_action.save()  # it is required to enable the historical recording
            script = Script.objects.get(pk=object_action.script.pk)
            script.code = script_code
            script.save()
        else:
            params["created_by"] = user
            script = Script.objects.create(code=script_code)
            params["script"] = script
            object_action = self.model_class.objects.create(**params)
        return object_action

    def get(self, action_id: int = None, user=None) -> Model:
        action = self.model_class.objects.get(id=action_id)
        if user and not validate_team_user(user, action.team):
            raise ObjectNotFound("Schedule Not Found")
        return action

    def get_query_set(self, params: Dict, user=None):
        name = params.get("name")
        order_by = params.get("order_by", "id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(name__icontains=name) | Q(description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        if user:
            object_list = object_list.filter(team__in=get_user_team(user))
        return object_list


class ScheduleExecutionBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(cls, model_class=ScheduleExecution) -> "ScheduleExecutionBusiness":
        return cls(model_class=model_class)

    def get(self, execution_id: int) -> Model:
        return self.model_class.objects.get(id=execution_id)

    def get_tickets(self, execution_id: int):
        return Ticket.objects.filter(schedule_execution__id=execution_id)

    def get_query_set(self, params: Dict, user=None):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(schedule__name__icontains=name)
                | Q(schedule__description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.filter().order_by(order_by)
        if user:
            object_list = object_list.filter(schedule__team__in=get_user_team(user))
        return object_list


class TicketBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(cls, model_class=Ticket) -> "TicketBusiness":
        return cls(model_class=model_class)

    def get(self, ticket_id: int) -> Model:
        return self.model_class.objects.get(id=ticket_id)

    def get_ticket_executions(self, ticket_id: int):
        return TicketActionLog.objects.filter(ticket__id=ticket_id)

    def get_ticket_parameters(self, ticket_id: int):
        return TicketParameter.objects.filter(ticket__id=ticket_id)

    def get_query_set(self, params: Dict, user=None):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        print(user)
        if name:
            object_list = self.model_class.objects.filter(
                Q(schedule__name__icontains=name)
                | Q(schedule__description__icontains=name)
                | Q(external_id=name)
            )
        else:
            object_list = self.model_class.objects.filter().order_by(order_by)
        if user:
            object_list = object_list.filter(schedule__team__in=get_user_team(user))
        return object_list

    def create(self, schedule: Schedule, schedule_execution: ScheduleExecution):
        return self.model_class.objects.create(
            schedule=schedule, schedule_execution=schedule_execution
        )

    def get_list_step_actions_forward(self, step: StepSchedule) -> List:
        total_step_schedule = StepSchedule.objects.filter(
            schedule=step.schedule
        ).count()
        return [
            order_execution
            for order_execution in range(step.execution_order, total_step_schedule)
        ]

    def create_task(
        self, ticket: Ticket, list_action_order_to_process: List = None, seconds_delay=0, team_worker=None, reprocess=False
    ):
        if not list_action_order_to_process:
            list_action_order_to_process = []
        if team_worker is None:
            team_worker = TeamWorker.objects.filter(team=ticket.schedule.team).first()
            
        if team_worker:
            queue_name = f"process-ticket-{team_worker.suffix_worker_name}"
        else:
            queue_name = "process-ticket"

        if reprocess:
            ticket.execution_status = EXECUTION_STATUS_QUEUE_RETRY
        else:
            ticket.execution_status = EXECUTION_STATUS_QUEUE
        ticket.save()
        tasks.process_ticket.apply_async(
            kwargs={
                "ticket_id": ticket.id,
                "list_action_order_to_process": list_action_order_to_process,
            },
            queue=queue_name,
            countdown=seconds_delay,
        )
