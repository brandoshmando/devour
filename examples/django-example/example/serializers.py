from rest_framework import serializers
from example.models import SimpleMessage

class SimpleMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleMessage
        fields = '__all__'
