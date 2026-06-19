from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from .models import GalleryCategory, GalleryImage


@cache_page(60 * 15)
def gallery(request):
    categories = GalleryCategory.objects.prefetch_related('images')
    active_category = request.GET.get('category')
    images = GalleryImage.objects.select_related('category', 'stylist')
    if active_category:
        images = images.filter(category__slug=active_category)
    return render(request, 'gallery/gallery.html', {
        'categories': categories,
        'images': images,
        'active_category': active_category,
    })
