from django.shortcuts import render,redirect
from django.http import JsonResponse
import requests

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone
from decouple import config


textCortexUrl = "https://api.textcortex.com/v1/texts/expansions"
text_cortex_api_key = config('TextCortexApiKey', default='')

textCortexHeaders = {
    "Content-Type": "application/json",
    "Authorization": f'Bearer {text_cortex_api_key}'
}



def generateResponse(message):
    payload = {
        "max_tokens": 512,
        "model": "chat-sophos-1",
        "n": 1,
        "source_lang": "en",
        "target_lang": "en",
        "temperature": 0.7,
        "text": message
    }   
    response = requests.request("POST", textCortexUrl, json=payload, headers=textCortexHeaders).json()
    return response['data']['outputs'][0]['text']

# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = generateResponse(message)

        chat = Chat(user=request.user,message=message,response=response,created_at=timezone.now())
        chat.save()
        return JsonResponse({'message':message,'response':response})
    return render(request,'chatbot.html',{'chats':chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error_message = "Invalid username or password"
            return render(request,'login.html',{'error_message':error_message})
    else:
        return render(request,'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except:
                error_message = "Error creating account"
                return render(request,'register.html',{'error_message':error_message})
        else:
            error_message = 'Password dont match'
            return render(request,'register.html',{'error_message':error_message})
    return render(request,'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')