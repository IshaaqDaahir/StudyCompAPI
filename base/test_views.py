from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from base.models import Room, Topic, Message
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'name': 'Test User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_user_login(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login(self):
        login_data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_get_users_list(self):
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_user_detail(self):
        url = reverse('user', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_user_profile(self):
        url = reverse('update-user')
        update_data = {
            'name': 'Updated Name',
            'bio': 'Updated bio'
        }
        response = self.client.put(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated Name')

class RoomViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_get_rooms_list(self):
        url = reverse('room-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_room_detail(self):
        url = reverse('room-detail', kwargs={'pk': self.room.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Room')

    def test_create_room(self):
        url = reverse('create-room')
        room_data = {
            'name': 'New Room',
            'description': 'New Description',
            'topic': 'Django'
        }
        response = self.client.post(url, room_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Room.objects.filter(name='New Room').exists())
        self.assertTrue(Topic.objects.filter(name='Django').exists())

    def test_update_room_as_host(self):
        url = reverse('update-room', kwargs={'pk': self.room.id})
        update_data = {
            'name': 'Updated Room',
            'description': 'Updated Description'
        }
        response = self.client.put(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertEqual(self.room.name, 'Updated Room')

    def test_update_room_as_non_host(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        other_token = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token.access_token}')
        
        url = reverse('update-room', kwargs={'pk': self.room.id})
        update_data = {'name': 'Hacked Room'}
        response = self.client.put(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_room_as_host(self):
        url = reverse('delete-room', kwargs={'pk': self.room.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Room.objects.filter(id=self.room.id).exists())

class MessageViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_get_messages_list(self):
        url = reverse('message-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_message(self):
        url = reverse('create-message', kwargs={'room_pk': self.room.id})
        message_data = {'body': 'New message'}
        response = self.client.post(url, message_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Message.objects.filter(body='New message').exists())
        # Check if user was added to participants
        self.assertIn(self.user, self.room.participants.all())

    def test_delete_own_message(self):
        url = reverse('message-detail', kwargs={'msg_pk': self.message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Message.objects.filter(id=self.message.id).exists())

    def test_delete_other_user_message(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        other_token = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token.access_token}')
        
        url = reverse('message-detail', kwargs={'msg_pk': self.message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class SearchViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Python Programming')
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Python Study Group',
            description='Learning Python together'
        )
        self.message = Message.objects.create(
            user=self.user,
            room=self.room,
            body='Hello Python developers!'
        )

    def test_search_rooms(self):
        url = reverse('search')
        response = self.client.get(url, {'q': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['rooms']), 1)
        self.assertEqual(len(response.data['topics']), 1)
        self.assertEqual(len(response.data['messages']), 1)

    def test_search_no_results(self):
        url = reverse('search')
        response = self.client.get(url, {'q': 'NonExistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['rooms']), 0)
        self.assertEqual(len(response.data['topics']), 0)
        self.assertEqual(len(response.data['messages']), 0)

class TopicViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Topic.objects.create(name='Python')
        Topic.objects.create(name='Django')

    def test_get_topics_list(self):
        url = reverse('topics-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)