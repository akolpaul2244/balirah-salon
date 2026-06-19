from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class ServiceCategory(models.Model):
    CATEGORY_TYPES = [
        ('barber', 'Barber Services'),
        ('nails', 'Nail Services'),
        ('combo', 'Combo Packages'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='FontAwesome icon class')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='services')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text='For variable pricing, set a max price')
    duration_minutes = models.PositiveIntegerField(help_text='Duration in minutes')
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    reengagement_category = models.CharField(
        max_length=50, blank=True,
        help_text='Category for re-engagement SMS: haircut, beard, nails, default'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__order', 'order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def price_display(self):
        if self.price_max:
            return f'UGX {self.price:,.0f} – {self.price_max:,.0f}'
        return f'UGX {self.price:,.0f}'

    @property
    def duration_display(self):
        h, m = divmod(self.duration_minutes, 60)
        if h and m:
            return f'{h}h {m}min'
        elif h:
            return f'{h}h'
        return f'{m}min'


class Promotion(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    services = models.ManyToManyField(Service, blank=True, related_name='promotions')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    banner_image = models.ImageField(upload_to='promotions/', null=True, blank=True)
    special_day = models.CharField(max_length=100, blank=True, help_text='e.g. Monday, Valentine, Christmas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
