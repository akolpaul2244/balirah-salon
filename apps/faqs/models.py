from django.db import models


class FAQCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'FAQ Category'
        verbose_name_plural = 'FAQ Categories'
        ordering = ['order']

    def __str__(self):
        return self.name


class FAQ(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.PROTECT, related_name='faqs')
    question = models.CharField(max_length=400)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category__order', 'order']

    def __str__(self):
        return self.question
