from django.contrib import admin
from .models import (
    Script,
    Schedule,
    Action,
    StepSchedule,
    ScheduleExecution,
    Ticket,
    TicketActionLog,
    ScheduleEnvironmentVariable,
    TicketParameter,
    TeamWorker,
)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "schedule", "execution_status", "created_date_ticket"]
    search_fields = ("id", "schedule", "execution_status")
    list_filter = ("schedule", "execution_status")


admin.site.register(TicketActionLog)
admin.site.register(Script)
admin.site.register(Schedule)
admin.site.register(Action)
admin.site.register(StepSchedule)
admin.site.register(ScheduleExecution)
admin.site.register(ScheduleEnvironmentVariable)
admin.site.register(TicketParameter)
admin.site.register(TeamWorker)