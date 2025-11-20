from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from base.models import Room, Topic, Message
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

class EndToEndWorkflowTest(TransactionTestCase):
    """Complete user journey from registration to room interaction"""
    
    def setUp(self):
        self.client = APIClient()

    def test_complete_user_workflow(self):
        # 1. User Registration
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'name': 'New User',
            'password1': 'securepass123',
            'password2': 'securepass123',
            'bio': 'I love learning!'
        }
        register_response = self.client.post(reverse('register'), register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # Extract tokens
        access_token = register_response.data['access']
        refresh_token = register_response.data['refresh']
        user_id = register_response.data['user']['id']
        
        # 2. Set authentication for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 3. Create a room
        room_data = {
            'name': 'Python Beginners',
            'description': 'Learning Python from scratch',
            'topic': 'Programming'
        }
        room_response = self.client.post(reverse('create-room'), room_data)
        self.assertEqual(room_response.status_code, status.HTTP_201_CREATED)
        room_id = room_response.data['id']
        
        # Verify topic was created
        self.assertTrue(Topic.objects.filter(name='Programming').exists())
        
        # 4. Send a message to the room
        message_data = {'body': 'Hello everyone! Excited to learn Python!'}
        message_response = self.client.post(
            reverse('create-message', kwargs={'room_pk': room_id}), 
            message_data
        )
        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        
        # 5. Verify user was added to room participants
        room = Room.objects.get(id=room_id)
        user = User.objects.get(id=user_id)
        self.assertIn(user, room.participants.all())
        
        # 6. Search for the room
        search_response = self.client.get(reverse('search'), {'q': 'Python'})
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(search_response.data['rooms']), 1)
        self.assertEqual(len(search_response.data['topics']), 1)
        self.assertEqual(len(search_response.data['messages']), 1)
        
        # 7. Update user profile
        profile_data = {
            'name': 'Updated User Name',
            'bio': 'Python enthusiast!'
        }
        profile_response = self.client.put(reverse('update-user'), profile_data)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # 8. Update room (as host)
        room_update_data = {
            'name': 'Advanced Python Study',
            'description': 'Deep dive into Python concepts'
        }
        room_update_response = self.client.put(
            reverse('update-room', kwargs={'pk': room_id}), 
            room_update_data
        )
        self.assertEqual(room_update_response.status_code, status.HTTP_200_OK)
        
        # 9. Get updated room details
        room_detail_response = self.client.get(
            reverse('room-detail', kwargs={'pk': room_id})
        )
        self.assertEqual(room_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(room_detail_response.data['name'], 'Advanced Python Study')

class MultiUserInteractionTest(TransactionTestCase):
    """Test interactions between multiple users"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create first user
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            name='User One'
        )
        self.token1 = RefreshToken.for_user(self.user1)
        
        # Create second user
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123',
            name='User Two'
        )
        self.token2 = RefreshToken.for_user(self.user2)
        
        # Create a room hosted by user1
        self.topic = Topic.objects.create(name='Django')
        self.room = Room.objects.create(
            host=self.user1,
            topic=self.topic,
            name='Django Study Group',
            description='Learning Django together'
        )

    def test_multi_user_room_interaction(self):
        # User2 joins room by sending a message
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2.access_token}')
        
        message_data = {'body': 'Hi everyone! Happy to join this group!'}
        message_response = self.client.post(
            reverse('create-message', kwargs={'room_pk': self.room.id}),
            message_data
        )
        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        
        # Verify user2 was added to participants
        self.room.refresh_from_db()
        self.assertIn(self.user2, self.room.participants.all())
        
        # User1 (host) sends a welcome message
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1.access_token}')
        
        welcome_message = {'body': 'Welcome to the group!'}
        welcome_response = self.client.post(
            reverse('create-message', kwargs={'room_pk': self.room.id}),
            welcome_message
        )
        self.assertEqual(welcome_response.status_code, status.HTTP_201_CREATED)
        
        # Verify there are now 2 messages in the room
        messages = Message.objects.filter(room=self.room)
        self.assertEqual(messages.count(), 2)
        
        # User2 tries to update room (should fail - not host)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2.access_token}')
        
        update_data = {'name': 'Hacked Room Name'}
        update_response = self.client.put(
            reverse('update-room', kwargs={'pk': self.room.id}),
            update_data
        )
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        
        # User2 tries to delete room (should fail - not host)
        delete_response = self.client.delete(
            reverse('delete-room', kwargs={'pk': self.room.id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

class AuthenticationFlowTest(TestCase):
    """Test complete authentication flows"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_logout_flow(self):
        # Login
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        login_response = self.client.post(reverse('login'), login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        # Use access token for authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_response = self.client.get(reverse('users'))
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # Logout
        logout_data = {'refresh': refresh_token}
        logout_response = self.client.post(reverse('logout'), logout_data)
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)
        
        # Try to use the same token (should fail after logout)
        profile_response_after_logout = self.client.get(reverse('users'))
        # Note: Token might still work until it expires, depending on implementation

    def test_token_refresh_flow(self):
        # Get initial tokens
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Use access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh token
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(reverse('token_refresh'), refresh_data)
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

class DataIntegrityTest(TestCase):
    """Test data relationships and constraints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_cascade_deletion(self):
        # Create room and message
        topic = Topic.objects.create(name='Test Topic')
        room = Room.objects.create(
            host=self.user,
            topic=topic,
            name='Test Room'
        )
        message = Message.objects.create(
            user=self.user,
            room=room,
            body='Test message'
        )
        
        # Delete room should cascade delete messages
        room.delete()
        self.assertFalse(Message.objects.filter(id=message.id).exists())
        
        # Topic should still exist (SET_NULL relationship)
        self.assertTrue(Topic.objects.filter(id=topic.id).exists())

    def test_room_participants_relationship(self):
        # Create room
        room_data = {
            'name': 'Test Room',
            'description': 'Test Description',
            'topic': 'Test Topic'
        }
        room_response = self.client.post(reverse('create-room'), room_data)
        room_id = room_response.data['id']
        
        # Send message (should add user to participants)
        message_data = {'body': 'Hello!'}
        self.client.post(
            reverse('create-message', kwargs={'room_pk': room_id}),
            message_data
        )
        
        # Verify user is in participants
        room = Room.objects.get(id=room_id)
        self.assertIn(self.user, room.participants.all())
        
        # Verify participant count
        self.assertEqual(room.participants.count(), 1)