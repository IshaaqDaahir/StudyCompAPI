from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.get_routes, name='api-routes'),
    
    # Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Users
    path('users/', views.get_users, name='users'),
    path('users/<int:pk>/', views.get_user, name='user'),
    path('users/update/', views.update_user, name='update-user'),
    
    # Rooms
    path('rooms/', views.room_list, name='room-list'),
    path('rooms/create/', views.create_room, name='create-room'),
    path('rooms/<int:pk>/', views.room_detail, name='room-detail'),
    path('rooms/<int:pk>/update/', views.update_delete_room, name='update-room'),
    path('rooms/<int:pk>/delete/', views.update_delete_room, name='delete-room'),
    
    # Messages
    path('rooms/<int:room_pk>/create-message/', views.create_message, name='create-message'),
    path('messages/', views.message_list, name='message-list'),
    path('messages/<int:msg_pk>/', views.message_detail, name='message-detail'),

    # Search
    path('search/', views.search, name='search'),

    # Topics
    path('topics/', views.topics_list, name='topics-list'),
]