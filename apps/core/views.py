import logging
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import mail_admins
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit

from .forms import ContactForm
from .models import SalonSettings, OpeningHours
from apps.services.models import Service, ServiceCategory
from apps.team.models import Stylist
from apps.gallery.models import GalleryImage
from apps.testimonials.models import Testimonial
from apps.blog.models import BlogPost

logger = logging.getLogger(__name__)


@cache_page(60 * 5)
def home(request):
    featured_services = Service.objects.filter(
        is_active=True, is_featured=True
    ).select_related('category')[:6]

    featured_testimonials = Testimonial.objects.filter(
        is_approved=True, is_featured=True
    ).select_related('service')[:6]

    featured_gallery = GalleryImage.objects.filter(
        is_featured=True
    ).select_related('category')[:8]

    team = Stylist.objects.filter(is_active=True)[:4]

    latest_posts = BlogPost.objects.filter(
        status='published'
    ).select_related('author', 'category')[:3]

    return render(request, 'core/home.html', {
        'featured_services': featured_services,
        'testimonials': featured_testimonials,
        'gallery_images': featured_gallery,
        'team': team,
        'latest_posts': latest_posts,
    })


@cache_page(60 * 60)
def about(request):
    team = Stylist.objects.filter(is_active=True).prefetch_related('specializations')
    return render(request, 'core/about.html', {'team': team})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                msg.ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                msg.ip_address = request.META.get('REMOTE_ADDR')
            msg.save()
            _notify_admin_contact(msg)
            messages.success(request, 'Your message has been sent. We\'ll get back to you shortly!')
            return redirect('core:contact')
    else:
        form = ContactForm()

    opening_hours = OpeningHours.objects.all()
    return render(request, 'core/contact.html', {
        'form': form,
        'opening_hours': opening_hours,
    })


def _notify_admin_contact(contact_msg):
    try:
        mail_admins(
            subject=f'New Contact: {contact_msg.subject}',
            message=(
                f'From: {contact_msg.name} <{contact_msg.email}>\n'
                f'Phone: {contact_msg.phone}\n\n'
                f'{contact_msg.message}'
            ),
        )
    except Exception as e:
        logger.error(f'Failed to notify admin of contact message {contact_msg.pk}: {e}')


def privacy_policy(request):
    salon = SalonSettings.get()
    return render(request, 'core/privacy_policy.html', {'salon': salon})


def terms_conditions(request):
    salon = SalonSettings.get()
    return render(request, 'core/terms_conditions.html', {'salon': salon})


def health_check(request):
    status = {"db": False, "cache": False}
    try:
        connection.ensure_connection()
        status["db"] = True
    except Exception as e:
        logger.error(f'Health check DB failure: {e}')
    try:
        cache.set("_health", "1", timeout=5)
        status["cache"] = cache.get("_health") == "1"
    except Exception as e:
        logger.error(f'Health check cache failure: {e}')
    all_ok = all(status.values())
    return JsonResponse(
        {"status": "ok" if all_ok else "degraded", **status},
        status=200 if all_ok else 503,
    )


def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)