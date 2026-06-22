from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from .models import Stylist

TEAM_CACHE_KEY = 'team_stylists_active'
TEAM_CACHE_TTL = 60 * 30


@require_http_methods(['GET'])
def team_list(request):
    stylists = cache.get(TEAM_CACHE_KEY)
    if stylists is None:
        stylists = list(
            Stylist.objects
            .filter(is_active=True)
            .prefetch_related('specializations')
            .only(
                'first_name', 'last_name', 'slug', 'role',
                'photo', 'years_experience', 'instagram', 'order',
            )
        )
        cache.set(TEAM_CACHE_KEY, stylists, TEAM_CACHE_TTL)
    return render(request, 'team/team_list.html', {'stylists': stylists})


@require_http_methods(['GET'])
def stylist_detail(request, slug):
    stylist = get_object_or_404(
        Stylist.objects.prefetch_related('specializations').filter(is_active=True),
        slug=slug,
    )
    return render(request, 'team/stylist_detail.html', {'stylist': stylist})