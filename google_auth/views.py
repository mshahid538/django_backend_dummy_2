import requests
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from apps.users.models import UserProfile

# import get_object_or_404()
from django.shortcuts import get_object_or_404

# Create your views here.


def googleoauth(request):
        google_callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"  # Replace with actual URL
        print(request)
        if request.method == "POST":
            data = request.POST  # Assuming the request data is being sent as POST
            
        # Make a request to the Google Allauth callback
            response = requests.post(google_callback_url, data=data)
            print('response=',response.content)
            
                    # Set CORS headers
            response_headers = {
                "Access-Control-Allow-Origin": "*",  # You might want to limit this to a specific origin
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
            }
            # Relay the response back to the frontend
            json_response = response.json()
            return JsonResponse(json_response, headers=response_headers)
    

        
    
        return JsonResponse({"status": "error"})



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
        get_user=UserProfile.objects.get(email=email)
        get_user.delete()
        return JsonResponse({
                'success':True,
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
           



       


