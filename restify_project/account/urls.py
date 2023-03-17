from django.urls import path
from . import views

urlpatterns = [
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/signup/', views.RegisterView.as_view(), name='signup'),
    path('api/forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reservation/', views.reservation, name='reservation'),
    path('login/', views.log_in, name='log_in'),
    path('api/profile/edit/', views.UserUpdateView.as_view(), name='profile_edit'),
    path('api/profile/', views.UserDetailView.as_view(), name='profile_detail'),
    path('user_comment_system/', views.user_comment_system, name='user_comment_system'),
]
