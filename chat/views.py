from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Acount, Chat, Group, Messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

@csrf_exempt
def saveUserSignal(request, id):
	acount = Acount.objects.get(pk=id)
	acount.acount_oneSignalId = request.POST['signal']

	acount.save()

	return HttpResponse('saved')

def sendNotify(acount, signalId, message, title):
	header = {
	    "accept": "application/json",
	    "Authorization": "Basic ODc3MTk1NmEtMWNiMy00ZDJiLThhNGUtZDRiYmE0ZWEyN2Rl",
	    "content-type": "application/json"
	}

	payload = {
		'app_id': 'c240b0ed-a771-4337-aded-bccbbdc57886',
		'include_player_ids': [signalId],
		'contents': {
			'en': message
		},
		'headings': {
			'en': title
		}
	}

	req = requests.post('https://onesignal.com/api/v1/notifications', headers=header, data=json.dumps(payload))
 
	acount.acount_notifyId = json.loads(req.content).get('id')
	acount.save()

#apresentação do site
def view_apresentation(request):
	if not request.user.is_authenticated:
		return render(request, 'apresentation.html')
	else:
		return redirect('/home/' + str(request.user))

#login
def view_login(request):
	try:
		if request.method == 'POST':
			username = request.POST['username']
			password = request.POST['password']

			user = authenticate(username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('/home/' + str(request.user))

			else:
				return render(request, 'login.html', {
					'msg': 'usuário ou senha incorretos',
					'class': 'msg-error'
				})

		else:
			return render(request, 'login.html')

	except Exception as e:
		return render(request, 'login.html', {
			'msg': 'verificação CSRF falhou, tente novamente',
			'class': 'msg-error'
		})


#logout
def view_logout(request):
	logout(request)

	return redirect('/login/')

#registro
def view_register(request):
	if request.method == 'POST':
		personal   = request.POST['personal_name']
		username   = request.POST['username']
		email      = request.POST['email']
		password   = request.POST['password']
		c_password = request.POST['confirm_password']

		if password == c_password:
			try:
				user = User.objects.create_user(username=personal, email=email, password=password)
			except Exception as e:
				return render(request, 'register.html', {
					'msg': 'Nome de usuário já existe',
					'class': 'msg-error'
				})

			if user is not None:
				user.save()

				new_user = authenticate(username=personal, password=password)
				login(request, new_user)

				Acount.objects.create(acount_name=username, acount_unicName=personal, acount_user=request.user)

				return redirect('/home/' + str(request.user))

		else:
			return render(request, 'register.html', {
				'msg': 'senhas diferentes',
				'class': 'msg-error'
			})

	else:
		return render(request, 'register.html')

#página principal
def view_home(request, user_name):
	user = User.objects.get(username=user_name)
	if user.id != request.user.id:
		return render(request, '404error.html')

	acount = Acount.objects.get(acount_user=request.user)

	data = {
		'acount': acount
	}

	#carregar chats
	chats = takeChats(acount)
	if len(chats) != 0:
		data['chats'] = chats

	#carregar grupos
	groups = Group.objects.filter(group_users=acount)

	if len(groups) != 0:
		data['groups'] = groups

	#pesquisa de usuários
	if request.GET.get('search'):
		search = request.GET.get('search')
		search_results = Acount.objects.filter(acount_unicName__icontains=search, acount_private=False).exclude(
			acount_unicName=acount.acount_unicName
		)

		return JsonResponse({'search':list(search_results.values())})


	#atualização em tempo real da home
	if request.GET.get('home'):
		acount_id = request.GET.get('home')

		#separação de categorias no chat
		acount = Acount.objects.get(pk=acount_id)
		chats = takeChats(acount)

		data = {
			'chats': chats
		}

		return JsonResponse({'data':data})


	if request.GET.get('group'):
		acount_id = request.GET.get('group')
		acount = Acount.objects.get(pk=acount_id)

		group_results = Group.objects.filter(group_users=acount_id)

		group_view = []
		for group in group_results:
			messages = Messages.objects.filter(message_group=group).last()

			if Messages.objects.filter(message_group=group).count() == 0:
				group_view.append(True)
			else:
				viewed = False
				for view in messages.message_views.all():
					if view == acount:
						viewed = True

				group_view.append(viewed)

		data = {
			'group': list(group_results.values()),
			'groupView': group_view,
		}

		return JsonResponse({'data': data})

	if request.GET.get('perfil'):
		acount_id = request.GET.get('perfil')
		acount = list(Acount.objects.filter(pk=acount_id).values())

		return JsonResponse({'perfil': acount})

	return render(request, 'home.html', data)

def takeChats(acount):
	chats1 = Chat.objects.filter(chat_user1=acount)
	chats2 = Chat.objects.filter(chat_user2=acount)
	chats = chats1.union(chats2)

	chat_list = []
	chat_view = []

	for chat in chats:
		if Messages.objects.filter(message_chat=chat.id).count() >= 1:
			if chat.chat_user1.id == acount.id:
				chat_list.append(chat.chat_user2)
			elif chat.chat_user2.id == acount.id:
				chat_list.append(chat.chat_user1)

			message = Messages.objects.filter(message_chat=chat.id).last()
			if message.message_user == acount:
			    chat_view.append(True)
			else:
			    chat_view.append(message.message_visualize)

	chat_name = []
	chat_unicname = []
	chat_description = []
	chat_photo = []
	chat_id = []

	for chat in chat_list:
		chat_name.append(chat.acount_name)
		chat_unicname.append(chat.acount_unicName)
		chat_description.append(chat.acount_description)
		chat_photo.append(str(chat.acount_photo))
		chat_id.append(chat.id)

	chats_list = [
		chat_name,
		chat_unicname,
		chat_description,
		chat_photo,
		chat_id,
		chat_view
	]

	return chats_list

def view_perfil(request, user_name):
	user = User.objects.get(username=user_name)
	acount = Acount.objects.get(acount_user=user.id)

	userAcount = Acount.objects.get(acount_user=request.user)

	data = {
		'acount': acount,
		'userAcount': userAcount
	}

	return render(request, 'perfil.html', data)

def alter(request, user_id):
	if user_id != request.user.id:
		return render(request, '404error.html')

	acount = Acount.objects.get(acount_user=user_id)

	collum = request.POST['alter_collum']

	if collum == 'alter_name':
		value  = request.POST['alter_value']
		acount.acount_name = value
		acount.save()

		return HttpResponse('sucess')

	elif collum == 'alter_description':
		value  = request.POST['alter_value']
		acount.acount_description = value
		acount.save()

		return HttpResponse('secess')

	elif collum == 'alter_photo':
		value  = request.FILES['alter_value']
		acount.acount_photo = value
		acount.save()

		return HttpResponse('sucess')

	elif collum == 'private':
		value  = request.POST['alter_value']

		if value == '0':
			value = False
		else:
			value = True

		acount.acount_private = value
		acount.save()

		return HttpResponse('sucess')

	elif collum == 'theme':
		value  = request.POST['alter_value']
			
		print(value)

		if value == '0':
			value = False
		else:
			value = True

		acount.acount_darkTheme = value
		acount.save()

		return HttpResponse('sucess')

#verifica e cria uma sala, o que possíbilita o contato
def view_chat(request, acount_id, contact_id):
	acount = Acount.objects.get(pk=acount_id)
	contact = Acount.objects.get(pk=contact_id)

	if acount.acount_user != request.user or acount_id == contact_id:
		return render(request, '404error.html')

	if acount_id > contact_id:
		user1 = acount
		user2 = contact
	else:
		user2 = acount
		user1 = contact

	chat = Chat.objects.filter(chat_user1=user1, chat_user2=user2)

	if chat.exists() == False:
		chat = Chat.objects.create(chat_user1=user1, chat_user2=user2)

	chat = Chat.objects.get(chat_user1=user1, chat_user2=user2)

	data = {
		'chat': chat,
		'acount': acount,
		'contact': contact
	}

	return render(request, 'chat.html', data)

#envia mensagem
def sendMessage(request):
	message = request.POST['message']
	image = None
	if 'image' in request.FILES:
		image = request.FILES['image']
	user = Acount.objects.get(pk=request.POST['user_id'])
	chat = Chat.objects.get(pk=request.POST['chat_id'])

	if (len(message.replace('\n', '')) > 0 or image is not None):	
		Messages.objects.create(
			message_content=message,
			message_image=image,
			message_user=user,
			message_chat=chat,
			message_group=None
		)

		otherAcount = None
		if chat.chat_user1 == user:
			otherAcount = Acount.objects.get(pk=chat.chat_user2.id)
		else:
			otherAcount = Acount.objects.get(pk=chat.chat_user1.id)


		sendNotify(otherAcount, otherAcount.acount_oneSignalId, 'Você tem novas mensagens', 'Vekor')

	return HttpResponse('')

#pega a mensagem do banco de dados
def getMessage(request, chat):
	chat_details = Chat.objects.filter(pk=chat)

	if chat_details.exists():
		chat_details = Chat.objects.get(pk=chat)

		messages = Messages.objects.filter(message_chat=chat)
		vizualize_messages(request, messages)

		return JsonResponse({'message':list(messages.values())})

def alterMessage(request):
	operation = request.POST['alter_collum']
	message = Messages.objects.get(pk=request.POST['alter_id'])

	if operation == 'alter':
		message.message_content = request.POST['alter_value']
		message.save()

	elif operation == 'delete':
		message.delete()

	return HttpResponse('sucess')

def vizualize_messages(request, messages):
	acount = Acount.objects.get(acount_user=request.user)

	for message in messages:
		if message.message_visualize == False and message.message_user.id != acount.id:
			message.message_visualize = True
			message.save()

def view_newGroup(request):
	if request.user.is_authenticated == False:
		return render(request, '404error.html')

	acount = Acount.objects.get(acount_user=request.user.id)

	if request.GET.get('chats'):
		chats = takeChats(acount)

		return JsonResponse({
			'chats': chats
		})

	if request.GET.get('search'):
		value = request.GET.get('search')
		search_results = Acount.objects.filter(acount_unicName__icontains=value, acount_private=True).exclude(
			acount_unicName=acount.acount_unicName
		)

		return JsonResponse({'search': list(search_results.values())})

	return render(request, 'newGroup.html', {
		'acount': acount
	})

def createGroup(request):
	if request.user.is_authenticated == False:
		return render(request, '404error.html')

	name = request.POST['groupName']
	description = request.POST['groupDescription']
	peoples = None
	photo = None

	try:
		photo = request.FILES['groupPhoto']
	except:
		photo = 'default/default_group.png'

	try:
		peoples = request.POST['groupPeoples']
	except:
		peoples = None

	if name == '':
		name = 'Grupo'


	peoplesArray = peoples.split(',')
	peoplesList = []

	if len(list(peoples)) >= 1:
		for people in peoplesArray:
			peopleAcount = Acount.objects.get(pk=people)
			peoplesList.append(peopleAcount)

	acount = Acount.objects.get(acount_user=request.user.id)
	peoplesList.append(acount)

	new_group = Group()
	new_group.save()

	group = Group.objects.get(pk=new_group.id)
	group.group_name = name
	group.group_description = description
	group.group_photo = photo
	group.group_admins.add(acount.id)
	group.group_users.set(peoplesList)

	group.save()

	return HttpResponse('group created')

def verify_userGroup(request, groupId):
	partOfGroup = False

	if request.user.is_authenticated == False:
		return False

	group = Group.objects.get(pk=groupId)
	groupPeoples = group.group_users.all()
	acount = Acount.objects.get(acount_user=request.user.id)

	for people in groupPeoples:
		if people == acount:
			partOfGroup = True

	return partOfGroup

def view_group(request, groupId):
	if verify_userGroup(request, groupId) == False:
		return redirect(request, '404error.html')

	group = Group.objects.get(pk=groupId)
	acount = Acount.objects.get(acount_user=request.user.id)

	data = {
		'group': group,
		'acount': acount
	}

	return render(request, 'chatGroup.html', data)

def view_groupMenu(request, groupId):
	if verify_userGroup(request, groupId) == False:
		return render(request, '404error.html')

	group = Group.objects.get(pk=groupId)
	acount = Acount.objects.get(acount_user=request.user.id)

	data = {
		'group': group,
		'acount': acount
	}

	for admin in group.group_admins.all():
		if acount == admin:
			data['admin'] = True

	if request.GET.get('search'):
		value = request.GET.get('search')
		search_results = Acount.objects.filter(acount_unicName__icontains=value, acount_private=True).exclude(
			acount_unicName=acount.acount_unicName
		)

		peoplesGroup = []

		for result in search_results:
			partOfGroup = False
			for user in group.group_users.all():
				if result == user:
					partOfGroup = True
					break

			if partOfGroup == False:
				peoplesGroup.append(list(Acount.objects.filter(pk=result.id).values())[0])

		return JsonResponse({'search': peoplesGroup})

	return render(request, 'groupMenu.html', data)

def alterGroup(request, groupId):
	if verify_userGroup(request, groupId) == False:
		return redirect(request, '404error.html')

	group = Group.objects.get(pk=groupId)
	acount = Acount.objects.get(acount_user=request.user.id)

	collum = request.POST['alter_collum']

	if collum == 'alter_exit':
		value = request.POST['alter_value']
		group.group_users.remove(value)
		group.group_admins.remove(value)
		
		groupUserMessages = Messages.objects.filter(
			message_group=groupId,
			message_user=value
		)

		groupUserMessages.delete()

		group.save()

	is_admin = False
	for people in group.group_admins.all():
		if people == acount:
			is_admin = True
			break

	if is_admin == False:
		return HttpResponse('Você não tem permisões para executar a ação.')

	if collum == 'alter_photo':
		value = request.FILES['alter_value']
		group.group_photo = value

		group.save()

	elif collum == 'alter_name':
		value = request.POST['alter_value']
		group.group_name = value

		group.save()

	elif collum == 'alter_description':
		value = request.POST['alter_value']
		group.group_description = value

		group.save()

	elif collum == 'alter_turnAdmin':
		value = request.POST['alter_value']
		group.group_admins.add(value)

		group.save()

	elif collum == 'alter_removeAdmin':
		value = request.POST['alter_value']
		group.group_admins.remove(value)

		group.save()

	elif collum == 'alter_exclude':
		value = request.POST['alter_value']
		group.group_users.remove(value)

		groupUserMessages = Messages.objects.filter(
			message_group=groupId,
			message_user=value
		)

		groupUserMessages.delete()

		group.save()

	elif collum == 'alter_add':
		value = request.POST['alter_value']
		group.group_users.add(value)

		group.save()

	elif collum == 'alter_destroy':
		value = request.POST['alter_value']
		group.delete()

	return HttpResponse('sucess')

#envia mensagem
def sendMessageGroup(request):
	if verify_userGroup(request, request.POST['group_id']) == False:
		return redirect(request, '404error.html')

	content = request.POST['message']
	image = None
	if 'image' in request.FILES:
		image = request.FILES['image']
	user = Acount.objects.get(acount_user=request.POST['user_id'])
	group = Group.objects.get(pk=request.POST['group_id'])

	if (len(content.replace('\n', '')) > 0 or image is not None):
		message = Messages()

		message.message_content = content
		message.message_image = image
		message.message_user = user
		message.message_chat = None
		message.message_group = group

		message.save()

		message.message_views.add(user.id)

		for people in group.group_users.all():
			if people != user:
				sendNotify(people, people.acount_oneSignalId, "Você tem novas mensagens", "Vekor")

	return HttpResponse('')

#pega a mensagem do banco de dados
def getMessageGroup(request, groupId):
	if verify_userGroup(request, groupId) == False:
		return render(request, '404error.html')

	group_details = Group.objects.filter(pk=groupId)

	if group_details.exists():
		group_details = Group.objects.get(pk=groupId)
		messages = Messages.objects.filter(message_group=groupId)
		vizualize_groupMessages(request, messages, group_details)

		group = Group.objects.get(pk=groupId)
		groupPeoples = group.group_users.all()

		data = {
			'message': list(messages.values()),
			'contacts': list(groupPeoples.values())
		}

		return JsonResponse({'data':data})

def vizualize_groupMessages(request, messages, group):
	acount = Acount.objects.get(acount_user=request.user)

	addView = False

	for message in messages:
		if message.message_visualize == False and message.message_user.id != acount.id:
			for view in message.message_views.all():
				if acount != view:
					addView = True

			if addView:
				message.message_views.add(acount.id)

				if len(message.message_views.all()) == len(group.group_users.all()):
					message.message_visualize = True

				message.save()