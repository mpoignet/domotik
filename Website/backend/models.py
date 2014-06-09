from django.db import models


class Sensor(models.Model):
    class Meta:
        db_table = 'sensor'
    def __unicode__(self):
        if self.name:
            return self.name
        return self.address

    SENSOR_TYPE_CHOICES = (
        ('TH', 'Thermometer'),
        ('CU', 'Current Sensor'),
    )

    address = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    sType = models.CharField(max_length=2, choices=SENSOR_TYPE_CHOICES,
                             default='TH')


class Actuator(models.Model):
    class Meta:
        db_table = 'actuator'
    def __unicode__(self):
        if self.name:
            return self.name
        return self.address

    ACTUATOR_TYPE_CHOICES = (
        ('VA', 'Valve'),
    )
    address = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    aType = models.CharField(max_length=2, choices=ACTUATOR_TYPE_CHOICES,
                             default='VA')


class Record(models.Model):
    class Meta:
        db_table = 'record'
    def __unicode__(self):
        return str(self.date.strftime('%Y-%m-%d %H:%M:%S')) + ': ' + str(
            self.measure)

    sensor = models.ForeignKey(Sensor)
    date = models.DateTimeField(blank=False, null=False)
    measure = models.FloatField(blank=False, null=False)


class Room(models.Model):
    class Meta:
        db_table = 'room'
    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=100, blank=False, null=False)
    isControlled = models.BooleanField(default=True)
    temperature = models.FloatField(blank=False, null=False, default=20)
    sensor = models.ForeignKey(Sensor)
    actuator = models.ForeignKey(Actuator, null=True)


class Watcher(models.Model):
    class Meta:
        db_table = 'watcher'
    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=100, blank=False, null=False)
    WATCHER_TYPE_CHOICES = (
        ('EXT', 'Exterior'),
        ('CON', 'Consumption'),
    )
    wtype = models.CharField(max_length=3, choices=WATCHER_TYPE_CHOICES,
                             default='EXT')
    sensor = models.ForeignKey(Sensor)

