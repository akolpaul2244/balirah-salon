from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from apps.core.sitemaps import (
    StaticViewSitemap, ServiceSitemap, TeamSitemap, BlogSitemap, GallerySitemap
)

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'team': TeamSitemap,
    'blog': BlogSitemap,
    'gallery': GallerySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('services/', include('apps.services.urls', namespace='services')),
    path('bookings/', include('apps.bookings.urls', namespace='bookings')),
    path('team/', include('apps.team.urls', namespace='team')),
    path('gallery/', include('apps.gallery.urls', namespace='gallery')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('testimonials/', include('apps.testimonials.urls', namespace='testimonials')),
    path('faqs/', include('apps.faqs.urls', namespace='faqs')),
    path('api/v1/', include('apps.core.api_urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('.well-known/security.txt', TemplateView.as_view(template_name='security.txt', content_type='text/plain')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = 'apps.core.views.error_400'
handler403 = 'apps.core.views.error_403'
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
