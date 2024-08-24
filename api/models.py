from django.db import models


class StoreZone(models.Model):
    store_id=models.CharField(max_length=50,primary_key=True)
    timezone_str=models.CharField(max_length=50,null=True,blank=True)
    def __str__(self):
        return self.store_id
    
class StoreHour(models.Model):
    store_id=models.ForeignKey(StoreZone,on_delete=models.CASCADE,related_name='business_hours')
    dayOfWeek=models.IntegerField()
    start_time_local=models.TimeField()
    end_time_local=models.TimeField()
    def __str__(self):
        return f'{self.store_id.store_id}-{self.dayOfWeek}'
    
class StoreStatus(models.Model):
    store = models.ForeignKey(StoreZone, on_delete=models.CASCADE, related_name="status_logs")
    status = models.CharField(max_length=100)
    timestamp = models.DateTimeField(verbose_name="Time Stamp in UTC",null=True,blank=True)

    def get_local_timestamp(self):
        return self.timestamp.astimezone(self.store.timezone_str)
    
    def __str__(self):
        return f"{self.store.store_id} - {self.status} - {self.timestamp}"

class ReportStatus(models.IntegerChoices):
    PENDING = 0
    COMPLETED = 1
    
class StoreReport(models.Model):
    report_id = models.CharField(max_length=100,primary_key=True)
    status = models.IntegerField(choices=ReportStatus.choices)
    report_url = models.FileField(upload_to="reports",null=True,blank=True)