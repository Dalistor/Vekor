"""rtc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from chat import views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.view_apresentation, name='apresentation'),
    path('login/', views.view_login, name='login'),
    path('logout/', views.view_logout, name='logout'),
    path('register/', views.view_register, name='register'),
    path('home/<str:user_name>', views.view_home, name='home'),
    path('saveUserSignal/<int:id>', views.saveUserSignal),
    path('OneSignalSDKWorker.js', TemplateView.as_view(template_name='onesignal/OneSignalSDKWorker.js', content_type='application/x-javascript')),
    path('perfil/<str:user_name>', views.view_perfil, name='perfil'),
    path('alter/<int:user_id>', views.alter, name='alter'),
    path('chat/<int:acount_id>/<int:contact_id>', views.view_chat, name='chat'),
    path('newGroup/', views.view_newGroup, name='newGroup'),
    path('createGroup/', views.createGroup, name='createGroup'),
    path('group/<int:groupId>', views.view_group, name='group'),
    path('groupMenu/<int:groupId>', views.view_groupMenu, name='groupMenu'),
    path('alterGroup/<int:groupId>', views.alterGroup, name='alterGroup'),
    path('send/', views.sendMessage, name='send'),
    path('alterMessage/', views.alterMessage, name='alterMessage'),
    path('groupSend/', views.sendMessageGroup, name='sendGroup'),
    path('get/<int:chat>', views.getMessage, name='get'),
    path('groupGet/<int:groupId>', views.getMessageGroup, name='groupGet'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
