import requests
import datetime
import json
import pytz
from django.http import JsonResponse
from apps.users.models import UserProfile
from rest_framework import status
from django.shortcuts import render,HttpResponse
#from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
# Create your views here.
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests

#Basically acts as a proxy between frontend and main callback function provided by allauth package 
def googleoauth(request):
        try:
            # print(request.POST)
            id_token_data = request.POST['id_token']
            CLIENT_ID = "322302178356-qeiht1u6u98b1n42rku6aen4ficbjp6r.apps.googleusercontent.com"
            idinfo = id_token.verify_oauth2_token(id_token_data, requests.Request(), CLIENT_ID)
            # print(idinfo)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Here you can create a user session or perform any other necessary actions.
            username=idinfo['name']
            email=idinfo['email']
            password ="some_password" #since the table has not null property
            # print(email)
            
            try:
                user=UserProfile.objects.get(email=email)
            except:
                user=None


            print(user)
            if user is not None:
                
                token, created = Token.objects.get_or_create(user=user)
                
               
               
                utc_now = datetime.datetime.utcnow()
                utc_now = utc_now.replace(tzinfo=pytz.utc)
                token.created = utc_now
                token.save()
                return JsonResponse({
                    'token': token.key,
                    'username':username,
                    'id': str(user.pk),
                    'pricing_tier': str(user.pricing_tier),
                    'email': str(user.email),
                    'trial_count': user.trial_count
                })
            else:
                
                user = UserProfile(username=username)
                user.set_password(password)
                user.email = email
                user.trial_count = 3
                user.save()

                token = Token.objects.create(user=user)

                return JsonResponse({
                     'msg': "register succeeds",
                     'token': token.key,
                    'username': str(user.username),
                    'id': str(user.pk),
                    'pricing_tier': str(user.pricing_tier),
                    'email': str(user.email),
                    'trial_count': user.trial_count,
                })


            
        except ValueError:
            return JsonResponse({'error': 'Invalid token.'}, status=400)









def reset(request):
   
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']
        confirm=request.POST['confirm']
        if (password!=confirm):
            return JsonResponse({
                'success':False,
                'msg':"password and confirm password not matches",
            })
        get_user=UserProfile.objects.get(email=email)
        if get_user is not None:
            get_user.set_password(password)

            get_user.save()
            print("true")
            return JsonResponse({
                'success':True,
            })
        else:
                 return JsonResponse({
                'success':False,
                'msg':"No email exists",
                   })
            





def remove(request):
    if request.method == "POST":
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        get_user=UserProfile.objects.get(email=email)
        user_name=get_user.username
        if password == confirm_password:

           
            get_user = authenticate(username=user_name, password=password)
            if get_user is not None:

                get_user.delete()
                return JsonResponse({
                    'success':True,
                })
            else:
                return JsonResponse({
                    'success':False,
                    'msg':'password didnot matched in database'
                })
        else:
            return JsonResponse({
                'success':False,
                'msg':'password and confirm password not matched'
            })



def reset_name(request):
   
    if request.method == 'POST':

        username=request.POST['username']
        newusername=request.POST['newusername']
        get_user=UserProfile.objects.get(username=username)
        get_user.username=newusername
        try:
          get_user.save()
          return JsonResponse({
                'success':True,
                'username':get_user.username
            })
        except:
            return JsonResponse({
                'success':False,
                'msg':"username already used please change it"
            })
            


def reset_email(request):
    print(request.POST)
    if request.method == 'POST':
        email=request.POST['user_email']
        newemail=request.POST['newemail']
        print(newemail)
        try:
            new_get_user=UserProfile.objects.get(email=newemail)
        except:
            new_get_user=None

        if new_get_user is not None:
            
            return JsonResponse({
                'success':False,
                'msg':"email alraady used so try another "
            })
        get_user=UserProfile.objects.get(email=email)
        get_user.email=newemail
        
        try:
            get_user.save()
            return JsonResponse({
                'success':True,
                'user_email':get_user.email
            })

        except:
            return JsonResponse({
                'success':False,
                'msg':" email already used please change it"
            })
           



       


