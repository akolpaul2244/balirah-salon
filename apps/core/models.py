from django.db import models


class SalonSettings(models.Model):
    salon_name = models.CharField(max_length=200, default='Balirah Beauty Salon')
    tagline = models.CharField(max_length=300, blank=True)
    about_short = models.TextField(blank=True)
    about_full = models.TextField(blank=True)
    phone_primary = models.CharField(max_length=20, blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    google_maps_embed = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='branding/', null=True, blank=True)
    favicon = models.ImageField(upload_to='branding/', null=True, blank=True)
    hero_image = models.ImageField(upload_to='branding/', null=True, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    google_analytics_id = models.CharField(max_length=30, blank=True)
    privacy_policy = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Salon Settings'
        verbose_name_plural = 'Salon Settings'

    def __str__(self):
        return self.salon_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OpeningHours(models.Model):
    DAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    day = models.IntegerField(choices=DAYS, unique=True)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['day']
        verbose_name_plural = 'Opening Hours'

    def __str__(self):
        return f'{self.get_day_display()}: {"Closed" if self.is_closed else f"{self.open_time}–{self.close_time}"}'


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', 'created_at'])]

    def __str__(self):
        return f'{self.name} – {self.subject}'
