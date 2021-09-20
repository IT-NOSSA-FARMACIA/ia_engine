from django.db import migrations


def create_permission(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type = ContentType.objects.get(app_label="task_engine", model="task_engine")
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        name="Can View Automation",
        codename="view_automation",
    )
    group, _ = Group.objects.get_or_create(name="Automation Viewer")
    group.permissions.add(permission)


def delete_permission(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    Group.objects.filter(name="Automation Viewer").delete()
    content_type = ContentType.objects.get(app_label="task_engine", model="task_engine")
    Permission.objects.filter(
        content_type=content_type,
        name="Can View Automation",
        codename="view_automation",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("task_engine", "0010_create_change_permission"),
    ]
    operations = [
        migrations.RunPython(create_permission, delete_permission),
    ]
