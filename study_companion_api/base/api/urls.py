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
    path('users/', views.get_users, name='users'),
    path('user/<int:pk>/', views.get_user, name='user'),
    
    # Rooms
    path('rooms/optimized/', views.get_rooms_optimized, name='room-list'),
    path('rooms/optimized/<int:pk>/', views.get_room_optimized, name='room-detail'),
    
    # Messages
    path('rooms/<int:room_pk>/messages/', views.message_list, name='message-list'),
]