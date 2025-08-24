from rest_framework import serializers
from base.models import Room, Topic, Message, User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from django.conf import settings
DEBUG = settings.DEBUG

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'bio', 'avatar']
        
    def get_avatar(self, obj):
        if obj.avatar:
            # Return full URL for avatar
            request = self.context.get('request')
            if not DEBUG:
                # For production with S3 - return direct S3 URL
                return obj.avatar.url
            else:
                # For development - build absolute URI
                return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(),
        message="This email is already registered.")]
    )
    username = serializers.CharField(
    required=True,
    validators=[UniqueValidator(
        queryset=User.objects.all(),
        message="This username is already taken."
        )]
    )
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'name', 'bio')
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
            bio=validated_data.get('bio', '')
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    participants = UserSerializer(read_only=True, many=True)
    
    class Meta:
        model = Room
        fields = '__all__'
        extra_kwargs = {
            'topic': {'required': True},
            'name': {'required': True}
        }

    def create(self, validated_data):
        # The topic is already set in the view
        validated_data['host'] = self.context['request'].user
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    avatar = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'bio', 'avatar']
        extra_kwargs = {
            'bio': {'required': False},
            'name': {'required': False}
        }

    def update(self, instance, validated_data):
        # Handle file upload separately
        avatar = validated_data.pop('avatar', None)
        
        # Update other fields
        instance = super().update(instance, validated_data)
        
        # Update avatar if provided
        if avatar:
            instance.avatar = avatar
            instance.save()
        
        return instance
