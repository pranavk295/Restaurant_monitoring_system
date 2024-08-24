from rest_framework import serializers
from .models import StoreZone, StoreHour, StoreStatus,StoreReport

class StoreZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreZone
        fields = '__all__'

class StoreHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreHour
        fields = '__all__'

class StoreStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStatus
        fields = '__all__'
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model=StoreReport
        fields='__all__'