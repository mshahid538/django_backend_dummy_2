import datetime
import pytz
from django.shortcuts import redirect
from django.urls import reverse
from django.core.mail import BadHeaderError, send_mail, EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from smtplib import SMTPException
from . models import UserProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.users.forms import (
    UploadImageForm,
    ContactForm,
    UserInfoForm,
    ChangePwdForm,
    RegisterPostForm,
    ActivateForm,
    InstagramForm,
    UserPricingTierForm
)

from apps.users.models import UserProfile
from apps.users.tokens import account_activation_token, ExpiringTokenAuthentication

from apps.users.serializers import UserProfileSerializer
from apps.users.permissions import (
    MyUserRetrievePermissions,
    MyUserListPermissions
)

from backend.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD


class UserView(viewsets.ModelViewSet):
    """
    View to list all users or retrieve/update single user in the system.
    it also supports to update single user's info

    * Requires token authentication.
    * Permission to list all users is admin only.
    * Permission to a single user is that particular user or admin
    """
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [MyUserListPermissions]
        else:
            permission_classes = [MyUserRetrievePermissions]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['POST'])
    def update_user_info(self, request, pk=None):
        user = UserProfile.objects.get(id=pk)
        self.check_object_permissions(self.request, user)
        user_info_form = UserInfoForm(data=request.data, instance=user)
        if user_info_form.is_valid():
            user_info_form.save()
            return Response({
                'msg': "register succeeds",
                'username': str(user.username),
                'id': str(user.pk),
                'pricing_tier': str(user.pricing_tier),
                'email': str(user.email),
                'trial_count': user.trial_count,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failed"},
                            status=status.HTTP_406_NOT_ACCEPTABLE
                            )

    @action(detail=True, methods=['POST'])
    def upload_image(self, request, pk=None):
        user = UserProfile.objects.get(id=pk)
        self.check_object_permissions(self.request, user)
        # 处理用户上传的头像
        image_form = UploadImageForm(
            request.POST, request.FILES, instance=user)
        if image_form.is_valid():
            image_form.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failed"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def change_password(self, request, pk=None):
        user = UserProfile.objects.get(id=pk)
        self.check_object_permissions(self.request, user)
        pwd_form = ChangePwdForm(data=request.data)
        if pwd_form.is_valid():
            pwd1 = request.data["password1"]
            user = request.user
            user.set_password(pwd1)
            user.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response(pwd_form.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def save_ig_info(self, request, pk=None):
        user = UserProfile.objects.get(id=pk)
        self.check_object_permissions(self.request, user)
        ig_form = InstagramForm(data=request.data)
        if ig_form.is_valid():
            ig_id = request.data["ig_id"]
            ig_token = request.data["ig_token"]
            user = request.user
            user.ig_id = ig_id
            user.ig_token = ig_token
            user.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response(ig_form.errors,
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def update_user_pricing_tier(self, request, pk=None):
        user = UserProfile.objects.get(id=pk)
        self.check_object_permissions(self.request, user)
        user_pricing_tier_form = UserPricingTierForm(
            data=request.data, instance=user)
        if user_pricing_tier_form.is_valid():
            user_pricing_tier_form.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failed"},
                            status=status.HTTP_406_NOT_ACCEPTABLE
                            )


class RegisterView(APIView):
    """
    View to register a user

    * Requires token authentication.
    * Permission is anyone.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
      
        register_post_form = RegisterPostForm(data=request.POST)
        print(request.POST)
        if register_post_form.is_valid():
            user_name = register_post_form.cleaned_data["username"]
            password = register_post_form.cleaned_data["password"]
            email = register_post_form.cleaned_data["email"]
            user = UserProfile(username=user_name)
            user.set_password(password)
            user.email = email
            user.trial_count = 3
            user.save()
            print('data is save')

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
        else:
            error_msg = register_post_form.errors.as_json()
            print("error_msg: ", error_msg)
            error_msg_response = ""
            if "Username is used" in error_msg:
                error_msg_response += "Username is used! "
            if "Email is used" in error_msg:
                error_msg_response += "Email is used!"
            return Response({
                'msg': "register fails",
                'errors': error_msg
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


# FIXME: enable this RegisterView to have email register function
class RegisterViewBackup(APIView):
    """
    View to register a user

    * Requires token authentication.
    * Permission is anyone.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        register_post_form = RegisterPostForm(data=request.data)
        if register_post_form.is_valid():
            user_name = register_post_form.cleaned_data["username"]
            password = register_post_form.cleaned_data["password"]
            email = register_post_form.cleaned_data["email"]
            # 新建一个用户
            user = UserProfile(username=user_name)
            user.set_password(password)
            user.email = email
            user.is_active = False
            user.save()

            # Sends email to the user
            subject = 'Welcome to AStory.ai'
            message = f"""Hi {user.username}, 
            
            Thank you for registering in Astory.ai!
            Please click on the link to confirm your registration:
            https://astoryai.com/active?uid={urlsafe_base64_encode(force_bytes(user.pk))}&token={account_activation_token.make_token(user)}/
            
Thanks,
AStory.ai
            """
            email_from = f'AStory.ai <{EMAIL_HOST_USER}>'
            recipient_list = [user.email, ]
            try:
                send_mail(subject, message, email_from, recipient_list)
            except BadHeaderError:
                return Response({
                    'msg': "email header is wrong",
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            except SMTPException as e:  # It will catch other errors related to SMTP.
                print('There was an error sending an email.' + e)
            except:  # It will catch All other possible errors.
                print("Mail Sending Failed!")

            token = Token.objects.create(user=user)
            return Response({
                'msg': "register succeeds"
            }, status=status.HTTP_200_OK)
        else:
            error_msg = register_post_form.errors.as_json()
            error_msg_response = ""
            if "Username is used" in error_msg:
                error_msg_response += "Username is used! "
            if "Email is used" in error_msg:
                error_msg_response += "Email is used!"
            return Response({
                'msg': "register fails",
                'errors': error_msg_response
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class ActivateView(APIView):
    """
    View to Activate a user

    * Requires token authentication.
    * Permission is anyone.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        activate_form = ActivateForm(data=request.data)
        if activate_form.is_valid():
            uid = activate_form.cleaned_data["uid"]
            token = activate_form.cleaned_data["token"]
        try:
            user_id = force_text(urlsafe_base64_decode(uid))
            user = UserProfile.objects.get(pk=user_id)
        except(TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            new_token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': new_token.key,
                'username': str(user.username),
                'id': str(user.pk)
            })
        else:
            return Response('Activation link is invalid!')


class LogoutView(APIView):
    """
    View to logout a user

    * Requires token authentication.
    * Permission is anyone.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # simply delete the token to force a logout
        request.user.auth_token.delete()
        return Response({"msg": "登出成功"}, status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    """
    View to login a user

    * Requires token authentication.
    * Permission is anyone.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(reverse("index"))

        next = request.GET.get("next", "")
        response = {
            "next": next,
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

            email = request.POST['email']
            password = request.POST['password']
            try:
                email =UserProfile.objects.get(email=email)
            except:
                return Response({
                'msg': "No email found",
                }, status=status.HTTP_404_NOT_FOUND, ) 


            
            
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

                return Response({
                'msg': "Wrong username or password",
                }, status=status.HTTP_401_UNAUTHORIZED, ) 






        # if serializer.is_valid():
        #     user = serializer.validated_data['user']
        #     user_name = serializer.validated_data['username']
        #     token, created = Token.objects.get_or_create(user=user)
        #     print("hello")
        #     if not created:
        #         # update the created time of the token to keep it valid
                # utc_now = datetime.datetime.utcnow()
        #         utc_now = utc_now.replace(tzinfo=pytz.utc)
        #         token.created = utc_now
        #         token.save()

        #     return Response({
        #         'token': token.key,
        #         'username': str(user_name),
        #         'id': str(user.pk),
        #         'pricing_tier': str(user.pricing_tier),
        #         'email': str(user.email),
        #         'trial_count': user.trial_count
        #     })
        # else:
        #     return Response({
        #         'msg': "Wrong username or password",
        #     }, status=status.HTTP_401_UNAUTHORIZED, )


class ContactView(APIView):
    """
    Get an message from a user and send an email to the user and admin

    * Requires token authentication.
    * Permission is anyone.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        contact_form = ContactForm(data=request.POST)
        print(contact_form)
        if contact_form.is_valid():
            name = contact_form.cleaned_data["name"]
            message =""" 
    You have requested to change the password. Please click the link below to change the password if you have requested it, otherwise discard the request.
    Reset Password following this link:   'http://localhost:3000/password-reset.html'
"""
            email = contact_form.cleaned_data["email"]

            # Sends email to the user
            subject = f'Message from {name}'
            email_from = f'AStory.ai <{EMAIL_HOST_USER}>'

            email_message = EmailMessage(
                subject,
                message,
                email_from,
                [email],
                [email_from]
            )

            try:
                email_message.send()
            except BadHeaderError:
                return Response({
                    'msg': "email header is wrong",
                }, status=status.HTTP_406_NOT_ACCEPTABLE)
            return Response({
                'msg': 'Message is sent!'
            })
        else:
            return Response({
                'errors': contact_form.errors,
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


# NOT SUPPORTED for now:
class CustomAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(
                Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


def message_nums(request):
    """
    Add media-related context variables to the context.
    """
    if request.user.is_authenticated:
        return {'unread_nums': request.user.usermessage_set.filter(
            has_read=False).count()}
    else:
        return {}



