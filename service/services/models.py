from django.core.validators import MaxValueValidator
from django.db import models

from service.clients.models import Client


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()



class Plan(models.Model):
    Plan_types = (
        ('full','Full'),
        ('student','Student'),
        ('discount','Discount')
    )

    plan_type = models.CharField(choices=Plan_types, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service =models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)