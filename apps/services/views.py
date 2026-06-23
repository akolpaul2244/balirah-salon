from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Prefetch
from django.views.decorators.http import require_http_methods

from .models import ServiceCategory, Service, Promotion
from .constants import (
    SERVICE_LIST_CACHE_KEY, SERVICE_LIST_CACHE_TTL,
    PRICING_CACHE_KEY, PRICING_CACHE_TTL,
)


@require_http_methods(['GET'])
def service_list(request):
    categories = cache.get(SERVICE_LIST_CACHE_KEY)
    if categories is None:
        categories = list(
            ServiceCategory.objects
            .filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    'services',
                    queryset=Service.objects.filter(is_active=True).order_by('order', 'name'),
                )
            )
            .order_by('order', 'name')
        )
        cache.set(SERVICE_LIST_CACHE_KEY, categories, SERVICE_LIST_CACHE_TTL)

    now = timezone.now()
    active_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now,
    ).prefetch_related('services')

    return render(request, 'services/service_list.html', {
        'categories': categories,
        'active_promotions': active_promotions,
    })


@require_http_methods(['GET'])
def service_detail(request, slug):
    service = get_object_or_404(
        Service.objects.select_related('category'),
        slug=slug,
        is_active=True,
    )
    related = (
        Service.objects
        .filter(category=service.category, is_active=True)
        .exclude(pk=service.pk)
        .only('name', 'slug', 'price', 'price_max', 'duration_minutes', 'short_description', 'description')
        [:4]
    )
    return render(request, 'services/service_detail.html', {
        'service': service,
        'related_services': related,
    })


@require_http_methods(['GET'])
def pricing(request):
    categories = cache.get(PRICING_CACHE_KEY)
    if categories is None:
        categories = list(
            ServiceCategory.objects
            .filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    'services',
                    queryset=Service.objects.filter(is_active=True).order_by('order', 'name'),
                )
            )
            .order_by('order', 'name')
        )
        cache.set(PRICING_CACHE_KEY, categories, PRICING_CACHE_TTL)

    return render(request, 'services/pricing.html', {'categories': categories})


@require_http_methods(['GET'])
def promotions(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    active_promotions = (
        Promotion.objects
        .filter(is_active=True, start_date__lte=now, end_date__gte=now)
        .prefetch_related('services')
        .order_by('end_date')
    )

    todays_promotions = active_promotions.filter(
        start_date__lte=today_end,
        end_date__gte=today_start,
    )

    has_today_promo = todays_promotions.exists()

    return render(request, 'services/promotions.html', {
        'active_promotions': active_promotions,
        'has_today_promo': has_today_promo,
    })