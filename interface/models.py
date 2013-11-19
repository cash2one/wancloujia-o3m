from django.db import models

# Create your models here.

class LogEntity(models.Model):
    content = models.CharField(max_length=10240, default='')
    create = models.DateTimeField()

    class Meta:
        ordering = ('create',)