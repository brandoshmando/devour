from rest_framework import serializers
from example.models import SimpleMessage, Problem

class SimpleMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleMessage
        fields = '__all__'


class ProblemSerializer(serializers.ModelSerializer):
    solution = serializers.ReadOnlyField(source='solution.value')

    class Meta:
        model = Problem
        fields = '__all__'

    def to_representation(self, obj):
        attrs = super(ProblemSerializer, self).to_representation(obj)
        if not attrs.get('solution'):
            attrs['solution'] = 'Refresh your page!'
        return attrs
