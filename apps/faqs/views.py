from django.shortcuts import render
from .models import FAQCategory


def faq_list(request):
   
    categories = (
        FAQCategory.objects
        .prefetch_related('faqs')
        .filter(faqs__is_active=True)
        .distinct()
    )
    return render(request, 'faqs/faq_list.html', {'categories': categories})