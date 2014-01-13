from django.db import models

# Create your models here.
class OperationLog(models.Model):
    username = models.CharField(max_length=32)
    content = models.CharField(max_length=64)
    date = models.DateField()
