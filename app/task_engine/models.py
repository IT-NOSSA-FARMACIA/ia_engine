from typing import Dict, List, Tuple, Any
from django.db import models
from core.models import Team
from django.contrib.auth.models import User
from .choices import EXECUTION_STATUS_CHOICE, EXECUTION_STATUS_PENDING
from io import StringIO
from contextlib import redirect_stdout
from django.core import signing
import sys, traceback


class Script(models.Model):
    code = models.TextField()

    def __str__(self) -> str:
        return super().__str__()

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

    def __str__(self) -> str:
        return self.name
        # return super().__str__()

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

    def __str__(self) -> str:
        return self.name
        # return super().__str__()

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

    def __str__(self) -> str:
        return super().__str__()

    class Meta:
        db_table = "schedule_execution"


class Ticket(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    execution_status = models.CharField(
        max_length=2, choices=EXECUTION_STATUS_CHOICE, default=EXECUTION_STATUS_PENDING
    )

    def __str__(self) -> str:
        return super().__str__()

    class Meta:
        db_table = "ticket"


class TicketParameter(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)

    def __str__(self) -> str:
        return super().__str__()

    class Meta:
        db_table = "ticket_parameter"


class TicketActionLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.DO_NOTHING)
    execution_log = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return super().__str__()

    class Meta:
        db_table = "ticket_action_log"


class ScheduleEnvironmentVariable(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)

    def __str__(self) -> str:
        return super().__str__()

    def save(self):
        self.value = signing.dumps(self.value)
        return super().save()

    @property
    def load_value(self) -> str:
        return signing.loads(self.value)

    class Meta:
        db_table = "schedule_environment_variable"


# from django.core import signing
# signing.loads("InNlbmhhMTIzIg:1lzSdt:-nZQEqod0IMU7gXdrvmGBQ4ZKZ-ZXEsYHPOaCKJKQhY")
# signing.dumps(('senha123'))
