import pandas as pd
from django.contrib.auth.models import User
from .models import StoreZone,StoreHour,StoreStatus
import pytz
from datetime import datetime
csv_file_path_1='api/Data/StoreTimeZones.csv'
csv_file_path_2='api/Data/Menu_hours.csv'
csv_file_path_3='api/Data/StoreStatus.csv'
df1=pd.read_csv(csv_file_path_1)
df2=pd.read_csv(csv_file_path_2)
df3=pd.read_csv(csv_file_path_3)



# Populates StoreZone Table
for index,row in df1.iterrows():
    zone, created= StoreZone.objects.get_or_create(
        store_id=row['store_id'],
        timezone_str=row['timezone_str']
    )

# handles business hours overlap 
hashmap={}
for index,row in df2.iterrows():
    if f"{row['store_id']}-{row['day']}" not in hashmap:
        hashmap[f"{row['store_id']}-{row['day']}"]=[row['start_time_local'],row['end_time_local']]
    else:

        hashmap[f"{row['store_id']}-{row['day']}"][0]=max(hashmap[f"{row['store_id']}-{row['day']}"][0],row['start_time_local'])
        hashmap[f"{row['store_id']}-{row['day']}"][1]=min(hashmap[f"{row['store_id']}-{row['day']}"][1],row['end_time_local'])

# Populates StoreHour Table
for key,value in hashmap.items():
    start_time_local=value[0]
    end_time_local=value[1]
    store_id=key.split('-')[0]
    dayOfWeek=key.split('-')[1]
    # handles the case when the store id does not exist in the StoreZone table
    if not StoreZone.objects.filter(store_id=store_id):
        StoreZone.objects.create(store_id=store_id,timezone_str='America/Chicago')
    hours,created=StoreHour.objects.get_or_create(
        store_id=StoreZone.objects.get(store_id=store_id),
        dayOfWeek=dayOfWeek,
        start_time_local=start_time_local,
        end_time_local=end_time_local
    )



# Populates StoreStatus Table
for index,row in df3.iterrows():
    utc_time_str=row['timestamp_utc'].replace(' UTC',"")
    utc_time_naive=datetime.strptime(utc_time_str,"%Y-%m-%d %H:%M:%S.%f")
    utc_time=pytz.utc.localize(utc_time_naive)
    if not StoreZone.objects.filter(store_id=row['store_id']):
        StoreZone.objects.create(store_id=row['store_id'],timezone_str='America/Chicago')
    status, created= StoreStatus.objects.get_or_create(
    store=StoreZone.objects.get(store_id=row['store_id']),
    status=row['status'],
    timestamp=utc_time
    )