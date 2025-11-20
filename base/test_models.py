from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from base.models import User, Room, Topic, Message

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'name': 'Test User',
            'bio': 'Test bio'
        }

    def test_create_user(self):
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            name=self.user_data['name'],
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.check_password('testpass123'))

    def test_email_unique(self):
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='pass123'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='pass123'
            )

    def test_user_str_representation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.assertEqual(str(user), 'testuser')

class TopicModelTest(TestCase):
    def test_create_topic(self):
        topic = Topic.objects.create(name='Python')
        self.assertEqual(topic.name, 'Python')
        self.assertEqual(str(topic), 'Python')

class RoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.topic = Topic.objects.create(name='Python')

    def test_create_room(self):
        room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Python Study Group',
            description='Learning Python together'
        )
        self.assertEqual(room.name, 'Python Study Group')
        self.assertEqual(room.host, self.user)
        self.assertEqual(room.topic, self.topic)
        self.assertEqual(str(room), 'Python Study Group')

    def test_room_participants(self):
        room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room'
        )
        participant = User.objects.create_user(
            username='participant',
            email='participant@example.com',
            password='pass123'
        )
        room.participants.add(participant)
        self.assertIn(participant, room.participants.all())

class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.topic = Topic.objects.create(name='Python')
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room'
        )

    def test_create_message(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body='Hello everyone!'
        )
        self.assertEqual(message.body, 'Hello everyone!')
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.room, self.room)
        self.assertEqual(str(message), 'Hello everyone!')

    def test_message_truncation(self):
        long_message = 'a' * 100
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body=long_message
        )
        self.assertEqual(str(message), 'a' * 50)