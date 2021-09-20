from django.contrib import admin
from .models import Team
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

# class TeamAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'base', 'description']
#     search_fields = ['id', 'name', 'base', 'description']


# admin.site.register(Team, TeamAdmin)
admin.site.register(Team)
admin.site.register(Permission)
admin.site.register(ContentType)

# ContentType.objects.create(app_label="task_engine", model="task_engine")
# content_type = ContentType.objects.get(app_label="hot", model="change_permission")
# permission = Permission.objects.create(content_type=content_type, name="Can Change Integration", codename="change_integration")