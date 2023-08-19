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

#Basically acts as a proxy between frontend and main callback function provided by allauth package 
def googleoauth(request):
        google_callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"  # Replace with actual URL
        #print(request)
        if request.method == "POST":
            data = request.POST  # Assuming the request data is being sent as POST
        # Make a request to the Google Allauth callback
            response = requests.post(google_callback_url, data=data)
                    # Set CORS headers
            response_headers = {
                "Access-Control-Allow-Origin": "*",  # You might want to limit this to a specific origin
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
            }

            # Relay the response back to the frontend
            json_response = response.json()
            #Basically what we did is saved to db if user doesnot exist else just return few things by logging in this step is done to return the token as creating a token requres user data model object

            user_name =json_response.pdata.given_name 
            password ="some password" #since the table has not null property
            email =json_response.pdata.given_email
            user = authenticate(username=email, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                login(request,user)
                utc_now = datetime.datetime.utcnow()
                utc_now = utc_now.replace(tzinfo=pytz.utc)
                token.created = utc_now
                token.save()
                return Response({
                    'token': token.key,
                    'username': str(email.username),
                    'id': str(user.pk),
                    'pricing_tier': str(user.pricing_tier),
                    'email': str(user.email),
                    'trial_count': user.trial_count
                })
            else:
                user_name =user_name 
                password =password 
                email =email 
                user = UserProfile(username=user_name)
                user.set_password(password)
                user.email = email
                user.trial_count = 3
                user.save()

                token = Token.objects.create(user=user)

                return Response({
                     'msg': "register succeeds",
                     'token': token.key,
                    'username': str(user.username),
                    'id': str(user.pk),
                    'pricing_tier': str(user.pricing_tier),
                    'email': str(user.email),
                    'trial_count': user.trial_count,
                }, status=status.HTTP_200_OK)

        return JsonResponse({"status": "error"})
