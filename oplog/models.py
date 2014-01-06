from django.db import models

# Create your models here.
class op_log(models.Model):
    date = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=32)
    content = models.CharField(max_length=80)
    class Meta:
        ordering = ('-pk',)