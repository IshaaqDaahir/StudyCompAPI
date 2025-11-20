from django.test import TestCase
from django.contrib.auth import get_user_model
from base.models import Room, Topic, Message
from base.serializers import (
    UserSerializer, RegisterSerializer, RoomSerializer, 
    MessageSerializer, TopicSerializer, UserUpdateSerializer
)
from rest_framework.test import APIRequestFactory

User = get_user_model()

class UserSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            name='Test User',
            bio='Test bio',
            password='testpass123'
        )

    def test_user_serialization(self):
        request = self.factory.get('/')
        serializer = UserSerializer(self.user, context={'request': request})
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['name'], 'Test User')
        self.assertEqual(data['bio'], 'Test bio')
        self.assertIn('avatar', data)

class RegisterSerializerTest(TestCase):
    def test_valid_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'name': 'New User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'bio': 'New user bio'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_password_mismatch(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'name': 'New User',
            'password1': 'testpass123',
            'password2': 'differentpass',
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'name': 'New User',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class RoomSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Python')
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room',
            description='Test Description'
        )

    def test_room_serialization(self):
        request = self.factory.get('/')
        serializer = RoomSerializer(self.room, context={'request': request})
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Room')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['host']['username'], 'testuser')
        self.assertEqual(data['topic']['name'], 'Python')

    def test_room_creation_serializer(self):
        request = self.factory.post('/')
        request.user = self.user
        
        data = {
            'name': 'New Room',
            'description': 'New Description'
        }
        serializer = RoomSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())

class MessageSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Python')
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room'
        )
        self.message = Message.objects.create(
            user=self.user,
            room=self.room,
            body='Test message'
        )

    def test_message_serialization(self):
        request = self.factory.get('/')
        serializer = MessageSerializer(self.message, context={'request': request})
        data = serializer.data
        
        self.assertEqual(data['body'], 'Test message')
        self.assertEqual(data['user']['username'], 'testuser')
        self.assertEqual(data['room']['name'], 'Test Room')

    def test_message_creation(self):
        data = {'body': 'New message'}
        serializer = MessageSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class TopicSerializerTest(TestCase):
    def test_topic_serialization(self):
        topic = Topic.objects.create(name='Django')
        serializer = TopicSerializer(topic)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Django')
        self.assertIn('id', data)

class UserUpdateSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_update(self):
        data = {
            'name': 'Updated Name',
            'bio': 'Updated bio'
        }
        serializer = UserUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.name, 'Updated Name')
        self.assertEqual(updated_user.bio, 'Updated bio')

    def test_email_update_unique_validation(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        data = {'email': 'other@example.com'}
        serializer = UserUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)