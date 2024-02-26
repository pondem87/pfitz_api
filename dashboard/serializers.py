from rest_framework import serializers
from zimgpt.models import DailyMetrics

import logging

logger = logging.getLogger(__name__)

class DailyMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMetrics
        fields = '__all__'