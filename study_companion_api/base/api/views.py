from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from base.models import User, Room
from .serializers import (
    RoomSerializer, 
    UserSerializer, 
    RegisterSerializer, 
    MessageSerializer,
)
from base.models import Room, Topic, Message
from django.db.models import Q

# api/views.py
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer, TopicSerializer, MessageSerializer
from base.models import Room, Topic, Message

@api_view(['GET'])
def get_routes(request):
    routes = [
        'GET /api',
        'GET /api/topics_list/',
        'GET /api/search/',
        'GET /api/rooms/',
        'GET /api/rooms/:id',
        'POST /api/rooms/:id/message',
        'GET /api/messages/',
        'GET /api/users/',
        'GET /api/users/:id',
        'POST /api/token/',
        'POST /api/token/refresh/',
        'POST /api/register/',
        'POST /api/login/',
        'POST /api/logout/',
    ]
    return Response(routes)

@api_view(["GET"])
def topics_list(request):
    topics = Topic.objects.all()
    topics_serializer = TopicSerializer(topics, many=True)
    return Response(topics_serializer.data)

@api_view(['GET'])
def search(request):
    query = request.GET.get('q', '')
    
    # Search rooms
    rooms = Room.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(topic__name__icontains=query) |
        Q(host__username__icontains=query)
    )
    room_serializer = RoomSerializer(rooms, many=True)
    
    # Search topics
    topics = Topic.objects.filter(name__icontains=query)
    topic_serializer = TopicSerializer(topics, many=True)
    
    # Search messages (for activity feed)
    messages = Message.objects.filter(
        Q(body__icontains=query) |
        Q(room__name__icontains=query) |
        Q(user__username__icontains=query)
    )
    message_serializer = MessageSerializer(messages, many=True)
    
    return Response({
        'rooms': room_serializer.data,
        'topics': topic_serializer.data,
        'messages': message_serializer.data
    })

@api_view(['GET', 'POST'])
def room_list(request):
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsAuthenticated])
def room_detail(request, pk):
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if room.host != request.user:
            return Response({'error': 'You are not the host of this room'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if room.host != request.user:
            return Response({'error': 'You are not the host of this room'}, status=status.HTTP_403_FORBIDDEN)
        
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(request, email=email, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_user(request, pk):
    user = User.objects.get(pk=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_message(request, room_pk):
    try:
        room = Room.objects.get(pk=room_pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        message = MessageSerializer(data=request.data)
        if message.is_valid():
            message.save(user=request.user, room=room)
            room.participants.add(request.user)
            return Response(message.data, status=status.HTTP_201_CREATED)
        return Response(message.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def message_list(request):
    if request.method == 'GET':
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    