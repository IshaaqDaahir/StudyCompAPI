# Study Companion API - Agent Documentation

## Architecture

Django REST Framework application with modular structure:

```
study_companion_api/
├── base/                    # Core app (models, views, serializers, urls)
├── study_companion_api/     # Project settings
└── requirements.txt
```

## Models

- **User**: Custom model with email auth, profile fields (name, bio, avatar)
- **Room**: Study rooms with host, topic, participants, timestamps
- **Topic**: Simple categorization for rooms
- **Message**: Room messaging with user association

## Authentication

- JWT tokens (1h access, 1d refresh)
- Email-based login with reCAPTCHA
- Permission-based access control

## API Endpoints

```
# Auth
POST /api/register/
POST /api/login/
POST /api/logout/

# Users
GET  /api/users/
PUT  /api/users/update/

# Rooms
GET  /api/rooms/
POST /api/rooms/create/
PUT  /api/rooms/{id}/update/
DELETE /api/rooms/{id}/delete/

# Messages
POST /api/rooms/{id}/create-message/
GET  /api/messages/
DELETE /api/messages/{id}/

# Search
GET /api/search/?q={query}
GET /api/topics/
```

## Configuration

- **Database**: SQLite (dev), PostgreSQL (prod)
- **Storage**: Local (dev), AWS S3 (prod)
- **CORS**: Frontend origins allowed
- **Security**: HTTPS, secure cookies in production

## Key Features

- Multi-model search across rooms, topics, messages
- File upload handling for avatars
- Automatic room participation on messaging
- Host-only room management
- Author-only message deletion