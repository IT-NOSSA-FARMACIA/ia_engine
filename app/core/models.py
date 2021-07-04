from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=100)
    user = models.ManyToManyField(User)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return super().__str__()

    class Meta:
        db_table = "team"
