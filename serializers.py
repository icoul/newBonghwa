from .models import Contents
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    reg_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class ContentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contents
        fields = ('id', 'mention_index', 'mention_order', 'username', 'contents', 'image', 'created_date', 'deleted')
