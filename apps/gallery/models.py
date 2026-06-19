from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToCover


class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Gallery Categories'
        ordering = ['order']

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    category = models.ForeignKey(GalleryCategory, on_delete=models.PROTECT, related_name='images')
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='gallery/')
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 400)],
        format='JPEG',
        options={'quality': 80},
    )
    large = ImageSpecField(
        source='image',
        processors=[ResizeToCover(1200, 900)],
        format='JPEG',
        options={'quality': 90},
    )
    is_featured = models.BooleanField(default=False)
    is_before_after = models.BooleanField(default=False)
    stylist = models.ForeignKey(
        'team.Stylist', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='gallery_images'
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        indexes = [models.Index(fields=['category', 'is_featured'])]

    def __str__(self):
        return self.title or f'Gallery image {self.pk}'
