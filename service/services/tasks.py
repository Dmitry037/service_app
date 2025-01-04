import datetime
import time

from celery import shared_task
from celery_singleton import Singleton
from django.db import transaction
from django.db.models import F


@shared_task(base=Singleton)
def set_price(subscription_id):  # bcgjkmpetv id чтобы не упустить изменения объекта за то время пока таска в очереди
    from services.models import Subscription
    with transaction.atomic():

        subscription = Subscription.objects.select_for_update().filter(id=subscription_id).annotate(
            annotated_price=F('service__full_price') -
                            F('service__full_price') * F('plan__discount_percent') / 100.00).first()


        subscription.price = subscription.annotated_price
        subscription.save()
    # print("do smth")  мы что то делаем вне транзакцию эта часть работает парралельно

@shared_task(base=Singleton)
def set_comment(subscription_id):  # bcgjkmpetv id чтобы не упустить изменения объекта за то время пока таска в очереди
    from services.models import Subscription
    # print("do smth") мы что то делаем вне транзакцию эта часть работает парралельно
    with transaction.atomic():
        subscription = Subscription.objects.select_for_update().get(id=subscription_id)


        subscription.comment = str(datetime.datetime.now())
        subscription.save()
