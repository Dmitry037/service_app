from django.db.models import Prefetch, F, Sum
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.core.cache import cache
from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name',
                                                              'user__email'))
        )#.annotate(price=F('service__full_price')-
        #                  F('service__full_price')*F('plan__discount_percent')/100.00) делаем цену через annotate
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        price_cache_name = 'price_cache'
        price_cache = cache.get(price_cache_name)

        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(price_cache_name, total_price, 10)

        response_data = {'result': response.data}
        response_data['total_amount'] = queryset.aggregate(total=Sum('price')).get('total')
        response.data = response_data
        return response

