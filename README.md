# Study Companion API

A Django REST API for a study companion application that enables students to create study rooms, participate in discussions, and collaborate on various topics.

## 🚀 Features

- **User Authentication**: JWT-based authentication with registration, login, and logout
- **Study Rooms**: Create, update, delete, and join study rooms
- **Real-time Messaging**: Send and receive messages within study rooms
- **Topic Management**: Organize rooms by study topics
- **User Profiles**: Customizable user profiles with avatar uploads
- **Search Functionality**: Search across rooms, topics, and messages
- **File Uploads**: AWS S3 integration for avatar and media storage

## 🛠️ Tech Stack

- **Backend**: Django 5.2.4, Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: PostgreSQL (Production), SQLite (Development)
- **File Storage**: AWS S3 (Production), Local storage (Development)
- **Deployment**: Render.com
- **CORS**: Django CORS Headers

## 📋 Prerequisites

- Python 3.8+
- pip
- PostgreSQL (for production)
- AWS S3 account (for file uploads)

## 🔧 Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd study_companion_api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Render Configuration
RENDER_EXTERNAL_HOSTNAME=your-render-app-url.onrender.com
```

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📚 API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Users
- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/update/` - Update user profile

### Rooms
- `GET /api/rooms/` - List all rooms
- `POST /api/rooms/create/` - Create new room
- `GET /api/rooms/{id}/` - Get room details
- `PUT /api/rooms/{id}/update/` - Update room
- `DELETE /api/rooms/{id}/delete/` - Delete room

### Messages
- `GET /api/messages/` - List all messages
- `POST /api/rooms/{room_id}/create-message/` - Create message in room
- `GET /api/messages/{id}/` - Get message details
- `DELETE /api/messages/{id}/` - Delete message

### Topics & Search
- `GET /api/topics/` - List all topics
- `GET /api/search/?q={query}` - Search rooms, topics, and messages

## 🏗️ Project Structure

```
study_companion_api/
├── base/                          # Main app
│   ├── migrations/               # Database migrations
│   ├── models.py                # Data models
│   ├── serializers.py           # API serializers
│   ├── views.py                 # API views
│   ├── urls.py                  # App URLs
│   └── admin.py                 # Admin configuration
├── study_companion_api/          # Project settings
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   ├── asgi.py                  # ASGI configuration
│   └── storage_backends.py      # AWS S3 storage backends
├── media/                        # Local media files (development)
├── staticfiles/                  # Static files
├── requirements.txt              # Python dependencies
├── build.sh                     # Render build script
├── render.yaml                  # Render configuration
└── manage.py                    # Django management script
```

## 🗄️ Data Models

### User
- Custom user model extending AbstractUser
- Fields: name, email, bio, avatar
- Email-based authentication

### Room
- Study rooms for collaboration
- Fields: host, topic, name, description, participants
- Many-to-many relationship with users (participants)

### Topic
- Study topics for categorizing rooms
- Fields: name

### Message
- Messages within study rooms
- Fields: user, room, body, timestamps

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register/Login**: Get access and refresh tokens
2. **Protected Routes**: Include `Authorization: Bearer <access_token>` header
3. **Token Refresh**: Use refresh token to get new access token

## 🌐 CORS Configuration

Configured for:
- Production: `https://studycomp.vercel.app`
- Development: `http://localhost:3000`

## 📁 File Upload

- **Development**: Files stored locally in `media/` directory
- **Production**: Files uploaded to AWS S3 bucket
- **Supported**: Image files for user avatars

## 🚀 Deployment

### Render.com Deployment

1. **Connect Repository**: Link your GitHub repository to Render
2. **Environment Variables**: Set required environment variables in Render dashboard
3. **Database**: Create PostgreSQL database on Render
4. **Build**: Render will automatically run `build.sh` script

### Required Environment Variables for Production:
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
WEB_CONCURRENCY=4
```

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📝 API Usage Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "name": "John Doe",
    "password1": "securepassword123",
    "password2": "securepassword123"
  }'
```

### Create Room
```bash
curl -X POST http://localhost:8000/api/rooms/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "name": "Python Study Group",
    "description": "Learning Python together",
    "topic": "Programming"
  }'
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/rooms/1/create-message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "body": "Hello everyone! Ready to study?"
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Isiya Dahiru**
- Email: ishaqtafiyau@gmail.com

## 🔗 Links

- **Frontend**: [Study Companion Frontend](https://studycomp.vercel.app)
- **API Base URL**: [https://study-companion-api-25hw.onrender.com/api/](https://study-companion-api-25hw.onrender.com/api/)

## 📞 Support

For support, email ishaqtafiyau@gmail.com or create an issue in the repository.