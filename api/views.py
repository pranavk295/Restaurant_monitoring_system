import csv
import os
import tempfile
from celery import shared_task
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import uuid
from django.db.models import Max
import pytz
from datetime import timedelta
from .serializers import ReportSerializer
from .models import StoreHour,StoreReport,StoreZone,StoreStatus,ReportStatus

def convert_to_local(utc_time_str,timezone):
    '''Converts timestamp in utc to local time.'''
    local_timezone = pytz.timezone(timezone)
    local_time = utc_time_str.astimezone(local_timezone)
    return local_time


def generate_report(store):
    '''Calculates the uptime and downtime per store using a simple interpolation logic.'''
    uptime_last_hour=0
    uptime_last_week=0
    uptime_last_day=0
    downtime_last_hour=0
    downtime_last_week=0
    downtime_last_day=0
    current_time=StoreStatus.objects.aggregate(Max('timestamp'))

    current_time=convert_to_local(current_time['timestamp__max'],store.timezone_str)
    inBusiness=[]
    results=StoreStatus.objects.filter(store_id=store.store_id)

    for result in results:
        day=result.timestamp.weekday()
        local_time=convert_to_local(result.timestamp,result.store.timezone_str)
        timings=StoreHour.objects.filter(store_id=store,dayOfWeek=day).values()
        start_time=timings[0]['start_time_local']
        end_time=timings[0]['end_time_local']
        if not end_time<=local_time.time()<start_time:
            inBusiness.append(result)

    one_hour_before=[]
    for temp in inBusiness:
        local_time=convert_to_local(temp.timestamp,temp.store.timezone_str)
        if current_time>local_time >= current_time-timedelta(hours=1):
            if temp.status=='active':
                one_hour_before.append(temp)      
        if current_time>local_time >= current_time-timedelta(days=1):
            if temp.status=='active':
                uptime_last_day+=1
        if current_time>local_time >= current_time-timedelta(weeks=1):
            uptime_last_week+=1
    downtime_last_day=24-uptime_last_day
    if downtime_last_day<0:
        downtime_last_day=0
    if len(one_hour_before)>0:
        uptime_last_hour+=60
    else:
        downtime_last_hour+=60
    downtime_last_week=24*7-uptime_last_week
    return [store.store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week]


def create_csv(report,csv_data):
   '''Creates the CSV file from the report generated.'''
   with tempfile.TemporaryDirectory() as temp_dir:
        file_name = f"{report.pk}.csv"
        temp_file_path = os.path.join(temp_dir, file_name)

        with open(temp_file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["store_id", "last_one_hour_uptime", "last_one_day_uptime", "last_one_week_uptime", "last_one_hour_downtime", "last_one_day_downtime", "last_one_week_downtime"])
            for data in csv_data:
                csv_writer.writerow(data)
        report.report_url.save(file_name, open(temp_file_path, "rb"))
        report.status = ReportStatus.COMPLETED
        report.save()

@shared_task
def generate_report_task(report_id):
    '''Creates the report as a background task with the help of celery.'''
    report = StoreReport.objects.get(report_id=report_id)
    csv_data = []

    results = StoreZone.objects.all()
    # generates report for first 2000 stores.
    for store in results[:2000]:
        data = generate_report(store)
        csv_data.append(data)

    create_csv(report, csv_data)
    report.status = ReportStatus.COMPLETED
    report.save()


@api_view(['GET'])
def trigger_report(request):
    '''Handles 'trigger_report/' api request and returns unique report id to access the report once generated.'''
    r_id=str(uuid.uuid4())
    report=StoreReport.objects.create(report_id=r_id,status=ReportStatus.PENDING)
    generate_report_task.delay(report.report_id)

    return JsonResponse(status=200,data={'report_id':report.report_id})

@api_view(['GET'])
def get_report(request, report_id):
    '''Handles 'get_report/' api request.'''
    try:
        report = StoreReport.objects.get(report_id=report_id)
    except StoreReport.DoesNotExist:
        return JsonResponse(status=404, data={'error': 'Report not found'})
    
    if report.status == ReportStatus.COMPLETED:
        serializer = ReportSerializer(report)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    else:
        return JsonResponse(status=200, data={'report_status': 'Running'})