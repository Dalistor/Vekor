from django.urls import path
from . import views

urlpatterns = [
	path('', views.view_apresentation, name='apresentation'),
	path('login/', views.view_login, name='login'),
    path('logout/', views.view_logout, name='logout'),
    path('register/', views.view_register, name='register'),
    path('home/<str:user_name>', views.view_home, name='home'),
    path('perfil/<str:user_name>', views.view_perfil, name='perfil'),
    path('chat/<int:acount_id>/<int:contact_id>', views.view_chat, name='chat'),
    path('newGroup/', views.view_newGroup, name='newGroup'),
    path('group/<int:groupId>', views.view_group, name='group'),
    path('groupMenu/<int:groupId>', views.view_groupMenu, name='groupMenu'),
]