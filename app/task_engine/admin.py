from django.contrib import admin

# Register your models here.


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
)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "schedule", "execution_status", "created_date"]
    search_fields = ("id", "schedule", "execution_status")
    list_filter = ("schedule", "execution_status")


# class TeamAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'base', 'description']
#     search_fields = ['id', 'name', 'base', 'description']


# admin.site.register(Team, TeamAdmin)
# admin.site.register(Team)
admin.site.register(TicketActionLog)
admin.site.register(Script)
admin.site.register(Schedule)
admin.site.register(Action)
admin.site.register(StepSchedule)
admin.site.register(ScheduleExecution)
admin.site.register(ScheduleEnvironmentVariable)
admin.site.register(TicketParameter)
