from chat.models import *
from rest_framework import serializers

class AcountSerializer(serializers.ModelSerializer):
	class Meta:
		model = Acount
		fields = [
			'id',
			'acount_name',
			'acount_description',
			'acount_photo',
			'acount_user',
			'acount_oneSignalId',
			'acount_private',
			'acount_darkTheme'
		]

class ChatSerializer(serializers.ModelSerializer):
	class Meta:
		model = Chat
		fields = [
			'id',
			'chat_user1',
			'chat_user2'
		]

class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = [
			'id',
			'group_name',
			'group_description',
			'group_photo',
			'group_users',
			'group_admins'
		]

class MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Messages
		fields = [
			'id',
			'message_content',
			'message_image',
			'message_visualize',
			'message_views',
			'message_user',
			'message_chat',
			'message_group',
			'message_posted_at',
			'message_edited_at'
		]