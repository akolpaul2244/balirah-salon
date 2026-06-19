from django.db import models
from django.conf import settings


class Testimonial(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='testimonials'
    )
    client_name = models.CharField(max_length=200)
    client_photo = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    service = models.ForeignKey(
        'services.Service', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='testimonials'
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)], default=5
    )
    body = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['is_approved', 'is_featured'])]

    def __str__(self):
        return f'{self.client_name} – {self.rating}★'
