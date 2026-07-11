from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    destination = models.CharField(
        max_length=100
    )

    days = models.IntegerField()

    budget = models.IntegerField()

    preferences = models.TextField()

    plan = models.TextField()

    # ----------------------------
    # AI Budget Breakdown
    # ----------------------------

    hotel_budget = models.IntegerField(
        default=0
    )

    food_budget = models.IntegerField(
        default=0
    )

    transport_budget = models.IntegerField(
        default=0
    )

    activities_budget = models.IntegerField(
        default=0
    )

    shopping_budget = models.IntegerField(
        default=0
    )

    emergency_budget = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.destination