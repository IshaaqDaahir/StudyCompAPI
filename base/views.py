from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
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
    UserUpdateSerializer,
)
from base.models import Room, Topic, Message
from django.db.models import Q
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer, TopicSerializer, MessageSerializer
from base.models import Room, Topic, Message
from django.http import JsonResponse
import requests
from django.conf import settings

def verify_recaptcha(token):
    """Verify reCAPTCHA token with Google"""
    if not token or not settings.RECAPTCHA_SECRET_KEY:
        return False
    
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': token
        }
    )
    return response.json().get('success', False)

@api_view(['GET'])
def get_routes(request):
    routes = [
        'GET /api',
        'GET /api/topics/',
        'GET /api/search/',
        'POST /api/rooms/create/'
        'GET /api/rooms/',
        'GET /api/rooms/:id/',
        'POST /api/rooms/:id/update/',
        'POST /api/rooms/:id/delete/',
        'POST /api/rooms/:id/create-message/',
        'GET /api/messages/',
        'GET /api/messages/:id/',
        'GET /api/users/',
        'GET /api/users/:id/',
        'POST /api/token/',
        'POST /api/token/refresh/',
        'POST /api/register/',
        'POST /api/login/',
        'POST /api/logout/',
    ]
    return Response(routes)

def empty_response():
    return JsonResponse([], safe=False)  # Return empty array instead of 404

@api_view(["GET"])
def topics_list(request):
    topics = Topic.objects.all()
    if not topics.exists():
            return JsonResponse([], safe=False)
    topics_serializer = TopicSerializer(topics, many=True, context={'request': request})
    return Response(topics_serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def search(request):
    query = request.query_params.get('q', '')
    
    # Search rooms
    rooms = Room.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(topic__name__icontains=query) |
        Q(host__username__icontains=query)
    )
    room_serializer = RoomSerializer(rooms, many=True, context={'request': request})
    
    # Search topics
    topics = Topic.objects.filter(name__icontains=query)
    topic_serializer = TopicSerializer(topics, many=True, context={'request': request})
    
    # Search messages (for activity feed)
    messages = Message.objects.filter(
        Q(body__icontains=query) |
        Q(room__name__icontains=query) |
        Q(user__username__icontains=query)
    )
    message_serializer = MessageSerializer(messages, many=True, context={'request': request})
    
    return Response({
        'rooms': room_serializer.data,
        'topics': topic_serializer.data,
        'messages': message_serializer.data
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_room(request):
    # Get topic name from request data
    topic_name = request.data.get('topic', '').strip()

    if not topic_name:
        return Response('Topic is required', status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create the topic
    topic, created = Topic.objects.get_or_create(name=topic_name)

    # Prepare data for serializer
    data = request.data.copy()
    if 'topic' in data:
        del data['topic']  # Remove topic from serializer data
    
    serializer = RoomSerializer(
        data=data,
        context={'request': request}
    )

    if serializer.is_valid():
        serializer.save(host=request.user, topic=topic)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def room_list(request):
    if request.method == 'GET':
        rooms = Room.objects.all()
        if not rooms.exists():
            return JsonResponse([], safe=False)
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def room_detail(request, pk):
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RoomSerializer(room, context={'request': request})
        return Response(serializer.data)

@api_view(['PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_delete_room(request, pk):
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        if room.host != request.user:
            return Response('You are not the host of this room', status=status.HTTP_403_FORBIDDEN)

        # Handle topic update
        topic_name = request.data.get('topic')
        if topic_name:
            topic_name = topic_name.strip()
            if topic_name:
                topic, created = Topic.objects.get_or_create(name=topic_name)
                request.data['topic'] = topic.id
            else:
                return Response('Topic cannot be empty', status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RoomSerializer(room, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if room.host != request.user:
            return Response('You are not the host of this room', status=status.HTTP_403_FORBIDDEN)
        
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        # Verify reCAPTCHA
        recaptcha_token = request.data.get('recaptcha_token')
        if not verify_recaptcha(recaptcha_token):
            return Response(
                {'error': 'reCAPTCHA verification failed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user, context={'request': request})
            return Response({
                'user': user_serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    # Verify reCAPTCHA
    recaptcha_token = request.data.get('recaptcha_token')
    if not verify_recaptcha(recaptcha_token):
        return Response(
            {'error': 'reCAPTCHA verification failed'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    email = request.data.get('email')
    password = request.data.get('password')

    # Validate input
    if not email or not password:
        return Response(
            'Both email and password are required', 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Normalize email
    email = email.lower().strip()
    
    # Authenticate using email as username
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        if not user.is_active:
            return Response(
                'Account is disabled. Please contact support.', 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # This is optional - only needed if you want session-based auth too
        login(request, user)
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'user': user_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    # Check if email exists in the system
    if not User.objects.filter(email=email).exists():
        return Response(
            'No account found with this email address', 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response('The password you entered is incorrect', status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_user(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        logout(request)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(
            str(e), 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_user(request, pk):
    user = User.objects.get(pk=pk)
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    if not users.exists():
            return JsonResponse([], safe=False)
    serializer = UserSerializer(users, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user(request):
    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        # Handle file upload
        data = request.data.copy()
        
        # If avatar is being uploaded, handle it properly
        if 'avatar' in request.FILES:
            data['avatar'] = request.FILES['avatar']

        serializer = UserUpdateSerializer(
            user, 
            data=data,
            partial=True,  # Allow partial updates
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            # Return updated user with absolute URL
            user_serializer = UserSerializer(user, context={'request': request})
            return Response(user_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_message(request, room_pk):
    try:
        room = Room.objects.get(pk=room_pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            room.participants.add(request.user)
            
            # Save the message with the user and room
            serializer.save(user=request.user, room=room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def message_list(request):
    if request.method == 'GET':
        messages = Message.objects.all()
        if not messages.exists():
            return JsonResponse([], safe=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def message_detail(request, msg_pk):
    try:
        message = Message.objects.get(pk=msg_pk)

        if request.method == 'GET':
            serializer = MessageSerializer(message, context={'request': request})
            return Response(serializer.data)
        
        elif request.method == 'DELETE':
            if message.user != request.user:
                return Response(
                    'You can only delete your own messages',
                    status=status.HTTP_403_FORBIDDEN
                )
            message.delete()
            return Response(
                {'success': 'Message deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
    
    except Message.DoesNotExist:
        return Response(
            'Message not found',
            status=status.HTTP_404_NOT_FOUND
        )
    