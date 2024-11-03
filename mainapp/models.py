from django.db import models

# Create your models here.
class Data(models.Model):
    image = models.ImageField(upload_to='images/')
    file = models.FileField()