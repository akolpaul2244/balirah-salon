from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import cache_page
from .models import ServiceCategory, Service, Promotion


@cache_page(60 * 15)
def service_list(request):
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related(
        'services'
    ).filter(services__is_active=True).distinct()
    active_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
    ).prefetch_related('services')
    return render(request, 'services/service_list.html', {
        'categories': categories,
        'active_promotions': active_promotions,
    })


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related = Service.objects.filter(
        category=service.category, is_active=True
    ).exclude(pk=service.pk)[:4]
    return render(request, 'services/service_detail.html', {
        'service': service,
        'related_services': related,
    })


@cache_page(60 * 15)
def pricing(request):
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related(
        models_prefetch('services', queryset=Service.objects.filter(is_active=True))
    )
    return render(request, 'services/pricing.html', {'categories': categories})


def models_prefetch(field, queryset=None):
    from django.db.models import Prefetch
    return Prefetch(field, queryset=queryset)
