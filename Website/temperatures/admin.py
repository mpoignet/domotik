from django.contrib import admin
from temperatures.models import Device, Record

# Register your models here.

class RecordAdmin(admin.ModelAdmin):
    readonly_fields = ('date', 'measure')

class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('address', 'dType')


admin.site.register(Record, RecordAdmin)
admin.site.register(Device, DeviceAdmin)
