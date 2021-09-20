from django.db import migrations


def create_permission(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type = ContentType.objects.get(app_label="api_engine", model="api_engine")
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        name="Can View API",
        codename="view_api",
    )
    group, _ = Group.objects.get_or_create(name="API Viewer")
    group.permissions.add(permission)


def delete_permission(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    Group.objects.filter(name="API Viewer").delete()
    content_type = ContentType.objects.get(app_label="api_engine", model="api_engine")
    Permission.objects.filter(
        content_type=content_type,
        name="Can View API",
        codename="view_api",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api_engine", "0010_create_change_permission"),
    ]
    operations = [
        migrations.RunPython(create_permission, delete_permission),
    ]
