from copy import deepcopy
from typing import Dict, Type, List

from django.db.models import Model
from django.db.models import Q
from django.contrib.auth.models import User

from .choices import EXECUTION_STATUS_QUEUE
from .tasks import process_ticket
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
)

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
            Script.objects.filter(pk=object_schedule.script.pk).update(code=script_code)
        else:
            script = Script.objects.create(code=script_code)
            params["script"] = script
            params["created_by"] = user
            object_schedule = self.model_class.objects.create(**params)
        return object_schedule

    def update_step_actions(self, schedule: Schedule, actions_id: List):
        StepSchedule.objects.filter(schedule=schedule).delete()
        execution_order = 0
        for action in actions_id:
            if action:
                StepSchedule.objects.create(
                    schedule=schedule, action_id=action, execution_order=execution_order
                )
                execution_order += 1

    def get(self, schedule_id: int = None) -> Model:
        return self.model_class.objects.get(id=schedule_id)

    def get_query_set(self, params: Dict):
        name = params.get("name")
        order_by = params.get("order_by", "id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(name__icontains=name) | Q(description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        return object_list


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
            Script.objects.filter(pk=object_action.script.pk).update(code=script_code)
        else:
            params["created_by"] = user
            script = Script.objects.create(code=script_code)
            params["script"] = script
            object_action = self.model_class.objects.create(**params)
        return object_action

    def get(self, action_id: int = None) -> Model:
        return self.model_class.objects.get(id=action_id)

    def get_query_set(self, params: Dict):
        name = params.get("name")
        order_by = params.get("order_by", "id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(name__icontains=name) | Q(description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
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

    def get_query_set(self, params: Dict):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(schedule__name__icontains=name)
                | Q(schedule__description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
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

    def reprocess_ticket(self, ticket_id: int):
        ticket = self.get(ticket_id)
        ticket.execution_status = EXECUTION_STATUS_QUEUE
        ticket.save()
        process_ticket.apply_async(
            kwargs={"ticket_id": ticket.id}, queue="process-ticket"
        )
        return ticket

    def get_query_set(self, params: Dict):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(schedule__name__icontains=name)
                | Q(schedule__description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        return object_list
