from django.db import models


class MyData(models.Model):
    name = models.CharField(verbose_name='A Name', blank=True, max_length=255)
    number = models.IntegerField(verbose_name='A Number')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'MyData'
