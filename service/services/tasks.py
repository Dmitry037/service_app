import time

from celery import shared_task
from celery_singleton import Singleton
from django.db.models import F


@shared_task(base=Singleton)
def set_price(subscription_id):  # bcgjkmpetv id чтобы не упустить изменения объекта за то время пока таска в очереди
    from services.models import Subscription

    time.sleep(5)

    subscription = Subscription.objects.filter(id=subscription_id).annotate(
        annotated_price=F('service__full_price')-
              F('service__full_price')*F('plan__discount_percent')/100.00).first()
    subscription.price = subscription.annotated_price
    subscription.save()