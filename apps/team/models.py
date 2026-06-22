from django.db import models
from django.utils.text import slugify
import cloudinary
from cloudinary.models import CloudinaryField


class Stylist(models.Model):
    ROLE_CHOICES = [
        ('barber', 'Barber'),
        ('nail_tech', 'Nail Technician'),
        ('both', 'Barber & Nail Tech'),
        ('manager', 'Manager'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    specializations = models.ManyToManyField(
        'services.ServiceCategory', blank=True, related_name='stylists'
    )
    bio = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    photo = CloudinaryField(
        'photo',
        folder='balirah/team',
        transformation=[{'width': 600, 'height': 700, 'crop': 'fill', 'gravity': 'face'}],
        null=True,
        blank=True,
    )
    instagram = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'first_name']
        indexes = [models.Index(fields=['is_active', 'order'])]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_full_name())
        super().save(*args, **kwargs)

    @property
    def photo_url(self):
        if self.photo:
            return cloudinary.CloudinaryImage(str(self.photo)).build_url(
                width=300, height=350, crop='fill', gravity='face',
                quality='auto', fetch_format='auto'
            )
        return None

    @property
    def photo_url_large(self):
        if self.photo:
            return cloudinary.CloudinaryImage(str(self.photo)).build_url(
                width=600, height=700, crop='fill', gravity='face',
                quality='auto', fetch_format='auto'
            )
        return None

    @property
    def completed_appointments(self):
        return self.appointments.filter(status='completed').count()