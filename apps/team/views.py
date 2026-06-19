from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from .models import Stylist


@cache_page(60 * 30)
def team_list(request):
    stylists = Stylist.objects.filter(is_active=True).prefetch_related('specializations')
    return render(request, 'team/team_list.html', {'stylists': stylists})


def stylist_detail(request, slug):
    stylist = get_object_or_404(Stylist, slug=slug, is_active=True)
    return render(request, 'team/stylist_detail.html', {'stylist': stylist})
