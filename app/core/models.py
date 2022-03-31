from simple_history.models import HistoricalRecords

from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=100)
    slash_name = models.CharField(max_length=100)
    user = models.ManyToManyField(User)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "team"
