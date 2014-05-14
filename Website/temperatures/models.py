from django.db import models

# Create your models here.

class Data(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    t0 = models.FloatField(blank=True, null=True)
    t1 = models.FloatField(blank=True, null=True)
    t2 = models.FloatField(blank=True, null=True)
    t3 = models.FloatField(blank=True, null=True)
    t4 = models.FloatField(blank=True, null=True)
    c0 = models.FloatField(blank=True, null=True)
    def __unicode__(self):  # Python 3: def __str__(self):
        return str(self.date.strftime('%Y-%m-%d %H:%M:%S'))

    class Meta:
        managed = False
        db_table = 'data'