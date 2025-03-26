from django.db import models

# Create your models here.

class Writeup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    link = models.URLField()
    summary = models.TextField()

    def __str__(self):
        return self.name