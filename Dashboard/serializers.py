from rest_framework import serializers

from Application.models import *


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'