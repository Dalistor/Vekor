from django.db import models
from django.contrib.auth.models import User

class Acount(models.Model):
	acount_name = models.CharField(max_length=20)
	acount_unicName = models.CharField(max_length=20, unique=True)
	acount_description = models.TextField(max_length=25, default='Estou usando o Vekor :D', blank=True)
	acount_photo = models.ImageField(upload_to='images-perfil/', default='default/default_perfil.png')

	acount_user = models.ForeignKey(User, on_delete=models.CASCADE)

	acount_oneSignalId = models.CharField(max_length=40, null=True, blank=True)

	acount_private = models.BooleanField(default=False)
	acount_darkTheme = models.BooleanField(default=False) 

	def __str__(self):
		return self.acount_user.username


class Chat(models.Model):
	chat_user1 = models.ForeignKey('Acount', on_delete=models.PROTECT, related_name='chat_user1')
	chat_user2 = models.ForeignKey('Acount', on_delete=models.PROTECT, related_name='chat_user2')


class Group(models.Model):
	group_name = models.CharField(max_length=20, default='Grupo')
	group_description = models.TextField(max_length=1000, blank=True)
	group_photo = models.ImageField(upload_to='images-group/', default='default/default_group.png')

	group_users = models.ManyToManyField('Acount', related_name='group_users')
	group_admins = models.ManyToManyField('Acount', blank=True, related_name='group_admins')

	def __str__(self):
		return self.group_name

class Messages(models.Model):
	message_content = models.TextField(max_length=10000, blank=True)
	message_image = models.ImageField(upload_to='images-chat/', blank=True, null=True)
	message_visualize = models.BooleanField(default=False)
	message_views = models.ManyToManyField('Acount', related_name='message_views', blank=True)

	message_user = models.ForeignKey('Acount', on_delete=models.PROTECT)
	message_chat = models.ForeignKey('Chat', on_delete=models.CASCADE, blank=True, null=True)
	message_group= models.ForeignKey('Group', on_delete=models.CASCADE, blank=True, null=True)

	message_posted_at = models.DateTimeField(auto_now_add=True)
	message_edited_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.message_user.acount_name
