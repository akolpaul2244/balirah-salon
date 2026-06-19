from django.shortcuts import render
from django.views.decorators.cache import cache_page
from .models import FAQCategory, FAQ


@cache_page(60 * 60)
def faq_list(request):
    categories = FAQCategory.objects.prefetch_related(
        'faqs'
    ).filter(faqs__is_active=True).distinct()
    return render(request, 'faqs/faq_list.html', {'categories': categories})
