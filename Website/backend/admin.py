from django.contrib import admin

from backend.models import Sensor, Record


# Register your models here.

class RecordAdmin(admin.ModelAdmin):
    readonly_fields = ('date', 'measure')


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('address', 'sType')


admin.site.register(Record, RecordAdmin)
admin.site.register(Sensor, DeviceAdmin)
