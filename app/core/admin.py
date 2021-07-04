from django.contrib import admin
from .models import Team


# class TeamAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'base', 'description']
#     search_fields = ['id', 'name', 'base', 'description']


# admin.site.register(Team, TeamAdmin)
admin.site.register(Team)
