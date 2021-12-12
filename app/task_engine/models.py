from typing import Dict, Tuple, Any
from io import StringIO
from contextlib import redirect_stdout
from simple_history.models import HistoricalRecords


from django.urls import reverse
from django.core import signing
from django.db import models
from django.contrib.auth.models import User

from core.models import Team
from .choices import (
    EXECUTION_STATUS_CHOICE,
    EXECUTION_STATUS_PENDING,
    NOTIFICATION_TYPE_CHOICE,
    NOTIFICATION_TYPE_NEVER,
)

import sys
import traceback


class Script(models.Model):
    code = models.TextField()
    history = HistoricalRecords()

    def __str__(self) -> str:
        return str(self.id)

    def get_output(self, binds):
        return self.output.format(**binds)

    def execute(self, parm: Dict = {}) -> Tuple[bool, Any, str]:
        stdout = StringIO()
        stderr = StringIO()
        return_data = []
        with redirect_stdout(stdout):
            exec(self.code, globals())
            try:
                return_data = main(**parm)
            except Exception:
                with redirect_stdout(stderr):
                    traceback.print_exc(file=sys.stdout)
        script_log = stdout.getvalue() + stderr.getvalue()
        status = not bool(stderr.getvalue())
        return status, return_data, script_log

    class Meta:
        db_table = "script"


class Schedule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    days = models.IntegerField(null=True, blank=True, default=0)
    hours = models.IntegerField(null=True, blank=True, default=0)
    minutes = models.IntegerField(null=True, blank=True, default=0)
    cron = models.CharField(max_length=20, null=True, blank=True)
    last_execution = models.DateTimeField(null=True, blank=True)
    last_value = models.CharField(max_length=100, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="schedule_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="schedule_last_updated_by",
    )
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    notification_type = models.CharField(
        max_length=2, choices=NOTIFICATION_TYPE_CHOICE, default=NOTIFICATION_TYPE_NEVER
    )
    emails_to_notification = models.CharField(max_length=2000, null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name
        # return super().__str__()

    def get_html_hyperlink(self) -> str:
        schedule_link = reverse("task_engine:schedule", args=(self.id,))
        return f"<a href='{schedule_link}'>{self.name}</a>"

    class Meta:
        db_table = "schedule"


class Action(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=100)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="action_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="action_last_updated_by",
    )
    active = models.BooleanField(default=True)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name
        # return super().__str__()

    def get_html_hyperlink(self) -> str:
        action_link = reverse("task_engine:action", args=(self.id,))
        return f"<a href='{action_link}'>{self.name}</a>"

    class Meta:
        db_table = "action"


class StepSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="step_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="steo_last_updated_by",
    )
    execution_order = models.IntegerField(default=0)
    stoppable = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.action.name
        # return super().__str__()

    class Meta:
        db_table = "step_schedule"


class ScheduleExecution(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    execution_status = models.CharField(
        max_length=2, choices=EXECUTION_STATUS_CHOICE, default=EXECUTION_STATUS_PENDING
    )
    execution_log = models.TextField(blank=True, null=True)
    execution_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.schedule.name} - {self.execution_status}"

    def get_html_hyperlink(self) -> str:
        schedule_execution_link = reverse(
            "task_engine:schedule-execution", args=(self.id,)
        )
        return f"<a href='{schedule_execution_link}'>{self.id}</a>"

    class Meta:
        db_table = "schedule_execution"


class Ticket(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    schedule_execution = models.ForeignKey(
        ScheduleExecution, on_delete=models.CASCADE, blank=True, null=True
    )
    created_date_ticket = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    execution_status = models.CharField(
        max_length=2, choices=EXECUTION_STATUS_CHOICE, default=EXECUTION_STATUS_PENDING
    )

    def __str__(self) -> str:
        return f"{self.id} - {self.schedule.name} - {self.execution_status}"

    def get_html_hyperlink(self) -> str:
        ticket_link = reverse("task_engine:ticket", args=(self.id,))
        # schedule_link = reverse("schedule", args=(self.id, ))
        return f"<a href='{ticket_link}'>{self.id}</a>"

    class Meta:
        db_table = "ticket"


class TicketParameter(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.TextField()

    def __str__(self) -> str:
        value = self.value[0:50]
        if len(self.value) > 50:
            value += "..."
        return f"{self.ticket.id} - {self.name} - {value}"

    class Meta:
        db_table = "ticket_parameter"


class TicketActionLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.DO_NOTHING)
    execution_log = models.TextField(blank=True, null=True)
    execution_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.ticket.id} - {self.action.name}"

    class Meta:
        db_table = "ticket_action_log"


class ScheduleEnvironmentVariable(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        old_schedule_env = ScheduleEnvironmentVariable.objects.filter(
            id=self.id
        ).first()
        old_value = old_schedule_env.value if old_schedule_env else ""
        if self.value != old_value:
            self.value = signing.dumps(self.value)
        return super().save(*args, **kwargs)

    @property
    def load_value(self) -> str:
        return signing.loads(self.value)

    class Meta:
        db_table = "schedule_environment_variable"


# from django.core import signing
# signing.loads("InNlbmhhMTIzIg:1lzSdt:-nZQEqod0IMU7gXdrvmGBQ4ZKZ-ZXEsYHPOaCKJKQhY")
# signing.dumps(('senha123'))
