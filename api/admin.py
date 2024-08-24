from django.contrib import admin
from .models import StoreZone,StoreHour,StoreStatus,StoreReport

admin.site.register(StoreZone)
admin.site.register(StoreHour)
admin.site.register(StoreStatus)
admin.site.register(StoreReport)