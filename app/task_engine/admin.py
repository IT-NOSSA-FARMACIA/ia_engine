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
admin.site.register(Ticket)
admin.site.register(ScheduleEnvironmentVariable)
admin.site.register(TicketParameter)
