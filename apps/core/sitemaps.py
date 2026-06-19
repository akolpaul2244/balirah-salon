from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.services.models import Service
from apps.team.models import Stylist
from apps.blog.models import BlogPost
from apps.gallery.models import GalleryCategory


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'core:about', 'core:contact', 'services:list',
                'team:list', 'gallery:gallery', 'blog:list', 'bookings:book',
                'faqs:list', 'services:pricing']

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('services:detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_at


class TeamSitemap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return Stylist.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('team:detail', kwargs={'slug': obj.slug})


class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return BlogPost.objects.filter(status='published')

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at


class GallerySitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return GalleryCategory.objects.all()

    def location(self, obj):
        return reverse('gallery:gallery') + f'?category={obj.slug}'
