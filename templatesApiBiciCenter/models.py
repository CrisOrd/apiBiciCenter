from django.db import models

# Create your models here.

class Bike(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    