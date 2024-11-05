from django.db import models

# Create your models here.
class Data(models.Model):
    image = models.ImageField(upload_to='images/')
    file = models.FileField()
    preview_image = models.ImageField(upload_to='previews/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)