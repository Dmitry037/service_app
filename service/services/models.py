from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client
from services.tasks import set_price, set_comment


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):
        if not hasattr(self, '__full_price'):
            self.__full_price = self.full_price  # Инициализация при первом сохранении
        if self.pk is not None and self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)
        super().save(*args, **kwargs)
        self.__full_price = self.full_price

    def __str__(self):
        return f"{self.name}"


class Plan(models.Model):
    Plan_types = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    plan_type = models.CharField(choices=Plan_types, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        if not hasattr(self, '__discount_percent'):
            self.__discount_percent = self.discount_percent  # Инициализация при первом сохранении
        if self.pk is not None and self.discount_percent != self.__discount_percent:
            if self.subscriptions.exists():  # Проверяем наличие связанных подписок
                for subscription in self.subscriptions.all():
                    set_price.delay(subscription.id)
                    set_comment.delay(subscription.id)
        super().save(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def __str__(self):
        return f"{self.plan_type}"


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=50, default='')

    def __str__(self):
        return f"Subscription of {self.client} on {self.service}"