from django.contrib import admin
from temperatures.models import Data

# Register your models here.

class DataAdmin(admin.ModelAdmin):
    readonly_fields = ('date','t0','t1','t2','t3','t4','c0')
    list_display = ('date','t0','t1','t2','t3','t4','c0')


admin.site.register(Data, DataAdmin)
