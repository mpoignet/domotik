from django.db import models

# Create your models here.

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
