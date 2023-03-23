from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('chat/', views.index, name="index"),
    path('signup/', views.signup_user, name="signup_user"),
    path('login/', views.login_user, name="login_user"),
    path('logout/', views.logout_user, name="logout_user"),
    path('upload/file/', views.handleFileUpload, name="handleFileUpload"),
]
