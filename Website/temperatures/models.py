from django.db import models

# Create your models here.

# class Data(models.Model):
#     date = models.DateTimeField(blank=True, null=True)
#     t0 = models.FloatField(blank=True, null=True)
#     t1 = models.FloatField(blank=True, null=True)
#     t2 = models.FloatField(blank=True, null=True)
#     t3 = models.FloatField(blank=True, null=True)
#     t4 = models.FloatField(blank=True, null=True)
#     c0 = models.FloatField(blank=True, null=True)
#     def __unicode__(self):  # Python 3: def __str__(self):
#         return str(self.date.strftime('%Y-%m-%d %H:%M:%S'))

#     class Meta:
#         managed = False
#         db_table = 'data'


class Device(models.Model):
    def __unicode__(self):
        if(self.name):  
            return self.name
        return self.address

    DEVICE_TYPE_CHOICES = (
        ('TH', 'Thermometer'),
        ('CU', 'Current Sensor'),
    )

    address = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    dType = models.CharField(max_length=2, choices=DEVICE_TYPE_CHOICES, default='TH')

class Record(models.Model):
    def __unicode__(self):  
        return str(self.date.strftime('%Y-%m-%d %H:%M:%S')) + ': ' + str(self.measure)

    device = models.ForeignKey(Device)
    date = models.DateTimeField(blank=False, null=False)
    measure = models.FloatField(blank=False, null=False)
