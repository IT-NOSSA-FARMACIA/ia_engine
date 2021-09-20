from django.db import migrations


def create_permission(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="task_engine", model="task_engine"
    )
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        name="Can Change Automation",
        codename="change_automation",
    )
    group, _ = Group.objects.get_or_create(name="Automation Developers")
    group.permissions.add(permission)


def delete_permission(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    Group.objects.filter(name="Automation Developers").delete()
    content_type = ContentType.objects.get(app_label="task_engine", model="task_engine")
    Permission.objects.filter(
        content_type=content_type,
        name="Can Change Automation",
        codename="change_automation",
    ).delete()
    content_type.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("task_engine", "0009_historicalscript"),
    ]
    operations = [
        migrations.RunPython(create_permission, delete_permission),
    ]
