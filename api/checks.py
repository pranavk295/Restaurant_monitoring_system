
# Additional checks to handle missing data.
from .models import StoreHour,StoreZone
from datetime import datetime
r1=StoreZone.objects.all().values('store_id').distinct()
r2=StoreHour.objects.all().values('store_id').distinct()
count=0
# handles the case when the business hours are not reported for a store (for all days of the week).
for r in r1:
    if r not in r2:
        for i in range(7):
            StoreHour.objects.create(store_id=StoreZone.objects.get(store_id=r['store_id']),dayOfWeek=i,start_time_local='00:00:00',end_time_local='23:59:59')
        count+=1

r1=StoreZone.objects.all().values('store_id').distinct()
r2=StoreHour.objects.all().values('store_id').distinct()

# handles the case when the business hours are note reported for a store (for some days of the week)
for r in r1:
    curr_start_time='00:00:00'
    curr_end_time='23:59:59'
    for i in range(7):
        check=StoreHour.objects.filter(store_id=r['store_id'],dayOfWeek=i)
        if not check:
            StoreHour.objects.create(store_id=StoreZone.objects.get(store_id=r['store_id']),dayOfWeek=i,start_time_local=curr_start_time,end_time_local=curr_end_time)
        else:
            curr_start_time=check.values()[0]['start_time_local']
            curr_end_time=check.values()[0]['end_time_local']
