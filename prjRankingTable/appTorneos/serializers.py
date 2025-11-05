from appTorneos import serializers
from appTorneos.models import Ranking
from rest_framework import serializers


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = '__all__'