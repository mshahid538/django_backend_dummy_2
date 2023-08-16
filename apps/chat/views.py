import requests
import time
import os
from pathlib import Path
import threading
import shutil


from django.http import JsonResponse, FileResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from apps.chat.forms import UserInputTextForm, UploadFileForm, DownloadFileForm, TranslateFileForm
from apps.chat.models import UserInputText, OriginalFileModel, ConvertedFileModel
from apps.users.models import UserProfile
from apps.users.tokens import ExpiringTokenAuthentication
from apps.chat.serializers import OriginalFileModelSerializer, ConvertedFileModelSerializer
from apps.chat.utilities import handle_uploaded_file, file_path, send_translate_completion_email, send_translate_failure_email

lock = threading.Lock()

def transcribe(lock, user, converted_file_model, filename, max_spkr, download_path, lip_sync_enabled, target_language):
    print("***Processing File***")
    print(f"wait for a lock for {filename}")
    lock.acquire()
    print(f"acquire a lock {filename}")
    try: 
        time.sleep(20)
        converted_file_model.downloadable = True
        converted_file_model.save()  
        send_translate_completion_email(user.username, user.email, os.path.basename(download_path))       
    except Exception as error:
        print("An exception occurred:", error)
        # trial_count has been decreased by 1, but user doesn't get their result. add 1 to trial_count
        if not user.is_staff:
            user.trial_count += 1
            user.save()
        try: 
            send_translate_failure_email(user.username, user.email, os.path.basename(filename))
            converted_file_model.delete()
        except Exception as error: 
            print("An exception occurred:", error)
    print(f"release for a lock {filename}")
    lock.release()

def readHuggingface(text):
    headers = {
        'Authorization': 'Bearer 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',
        'Content-Type': 'application/json',
    }
    json_data = {
    'inputs': text,
    }
    url = 'https://mfbxpmuxnc0n7yql.us-east-1.aws.endpoints.huggingface.cloud'
    return requests.post(url,headers=headers, json=json_data)

class UserInputTextView(APIView):
    """
    View to generate result based on user's input

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        APIView.__init__(self, **kwargs)
    def post(self, request, *args, **kwargs):
        user = UserProfile.objects.get(username=request.user.get_username())

        if not user.is_staff and user.trial_count <= 0:
            return JsonResponse({
                "status": "fail",
                "msg": "usage limit reached"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        user_input_text_form = UserInputTextForm(data=request.data)

        if user_input_text_form.is_valid():
            user_input_text = user_input_text_form.cleaned_data["user_input_text"]
            speaker_id = 0

            # reuslt = readHuggingface(user_input_text).json()
            # generated_text = reuslt[0]['generated_text']
            generated_text = "大家好我是小鱼儿很高兴又跟大家见面了今天给大家带来的是"
            # generated_text = "大家是真的很不好"
            # batchs, control_values = preprocess_input(generated_text, speaker_id, self.preprocess_config)

            time0 = time.time()
            audio_path = "audio/spanish_chat_2p_30s.wav"
            # result, segs = transcribe(audio_path, 2, translate=True)

            # synthesize(self.model, 600000, self.configs, self.vocoder, batchs, control_values)
            time1 = time.time()
            # print("Time-> ", round(time1-time0, 3))
            # print("===results: \n", result)
            # print("---segs: \n", segs)

            user_input_text_model = UserInputText()
            user_input_text_model.user = request.user
            user_input_text_model.user_input_text = user_input_text
            user_input_text_model.save()
        
            return Response({
                "status": "success",
                "generated_text": generated_text,
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class UploadFileView(APIView):
    """
    Upload file to audio folder

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        username = request.user.get_username()
        user = UserProfile.objects.get(username=username)
        return JsonResponse({
                "status": "success",
                "trial_count": user.trial_count,
            }, status=status.HTTP_200_OK)
       
    def post(self, request, *args, **kwargs):
        user = UserProfile.objects.get(username=request.user.get_username())

        if not user.is_staff and user.trial_count <= 0:
            return JsonResponse({
                "status": "fail",
                "msg": "usage limit reached"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        upload_file_form = UploadFileForm(request.POST, request.FILES)
        if upload_file_form.is_valid():
            file = upload_file_form.cleaned_data['file']
            max_spkr= upload_file_form.cleaned_data['num_speaker']
            lip_sync_enabled = upload_file_form.cleaned_data['lip_sync_enabled']
            target_language = upload_file_form.cleaned_data['target_language']
            max_spkr=int(max_spkr)
            lip_sync_enabled = True if lip_sync_enabled == "1" else False
            print("===File: ", file.name)
            print("max_spkr: ", max_spkr)
            print("lip_sync_enabled: ", lip_sync_enabled)
            print("target_language", target_language)
            root, file_extension = os.path.splitext(file.name)
            filename = "audio/{}/{}{}".format(user.username, root, file_extension)
            filename = os.path.join(file_path, filename)
            idx = 1
            while (os.path.isfile(filename)):
                filename = "audio/{}/{}_{}{}".format(user.username, root, idx, file_extension)
                filename = os.path.join(file_path, filename)
                idx = idx + 1

            handle_uploaded_file(filename, file)

            original_file_model = OriginalFileModel()
            original_file_model.user = user
            original_file_model.filename = os.path.basename(filename)
            original_file_model.path = filename
            original_file_model.save()
        
            download_path = f"audio/{user.username}/{str(root)}_translate{file_extension}"
            download_path = os.path.join(file_path, download_path)
            idx = 1
            while (os.path.isfile(download_path)):
                print("saving: ", download_path)
                download_path = f"audio/{user.username}/{str(root)}_translate_{idx}{file_extension}"
                download_path = os.path.join(file_path, download_path)
                idx = idx + 1
            converted_file_model = ConvertedFileModel()
            converted_file_model.user = user
            converted_file_model.filename = os.path.basename(download_path)
            converted_file_model.path = download_path
            converted_file_model.downloadable = False
            converted_file_model.save()   
            
            shutil.copyfile(filename, download_path)

            thread = threading.Thread(
                target=transcribe, args=(lock, user, converted_file_model, filename, max_spkr, download_path, lip_sync_enabled, target_language)
            )
            thread.start()

            if not user.is_staff:
                user.trial_count -= 1
                user.save()

            return Response({
                "status": "success",
                "trial_count": user.trial_count
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        

class DownloadFileView(GenericAPIView):
    """
    Download file

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_type, *args, **kwargs):
        username = request.user.get_username()
        if file_type == "original":
            queryset = OriginalFileModel.objects.filter(user=request.user).order_by('-add_time')
            serializer = OriginalFileModelSerializer(queryset, many=True)
            return self.get_paginated_response(self.paginate_queryset(serializer.data))
        else: 
            queryset = ConvertedFileModel.objects.filter(user=request.user).order_by('-add_time')
            serializer = ConvertedFileModelSerializer(queryset, many=True)
            return self.get_paginated_response(self.paginate_queryset(serializer.data))

    def post(self, request, *args, **kwargs):        
        download_file_form = DownloadFileForm(data=request.data)
        if download_file_form.is_valid():
            filename = download_file_form.cleaned_data['filename']
            is_original = download_file_form.cleaned_data['is_original']
            # print("is_original: ", is_original)
            if is_original == "1":
                file_queryset = OriginalFileModel.objects.filter(filename=filename, user=request.user)
            else:
                file_queryset = ConvertedFileModel.objects.filter(filename=filename, user=request.user)
            # print("===filename: ", filename)
            # print("====file_queryset: ", file_queryset)

            response = FileResponse(open(file_queryset[0].path, 'rb'), as_attachment=True, content_type='video/mp4')

            return response
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class DeleteFileView(GenericAPIView):
    """
    Delete file

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):        
        download_file_form = DownloadFileForm(data=request.data)
        if download_file_form.is_valid():
            filename = download_file_form.cleaned_data['filename']
            is_original = download_file_form.cleaned_data['is_original']
            # print("is_original: ", is_original)
            if is_original == "1":
                file_queryset = OriginalFileModel.objects.filter(filename=filename, user=request.user)
            else:
                file_queryset = ConvertedFileModel.objects.filter(filename=filename, user=request.user)
            # print("===filename: ", filename)
            # print("====file_queryset: ", file_queryset)

            file_path = file_queryset[0].path
            while (os.path.isfile(file_path)):
                try:
                    os.remove(file_path)
                except:
                    print(f"something went wrong. cannot remove{file_path}")
                
            file_queryset.delete()

            if is_original == "1":
                queryset = OriginalFileModel.objects.filter(user=request.user).order_by('-add_time')
                serializer = OriginalFileModelSerializer(queryset, many=True)
                return self.get_paginated_response(self.paginate_queryset(serializer.data))
            else: 
                queryset = ConvertedFileModel.objects.filter(user=request.user).order_by('-add_time')
                serializer = ConvertedFileModelSerializer(queryset, many=True)
                return self.get_paginated_response(self.paginate_queryset(serializer.data))
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        

class UploadedFileTranslateView(GenericAPIView):
    """
    Translate uploaded file

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = UserProfile.objects.get(username=request.user.get_username())

        if not user.is_staff and user.trial_count <= 0:
            return JsonResponse({
                "status": "fail",
                "msg": "usage limit reached"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        translate_file_form = TranslateFileForm(request.POST, request.FILES)
        if translate_file_form.is_valid():
            filename = translate_file_form.cleaned_data['filename']
            max_spkr= translate_file_form.cleaned_data['num_speaker']
            lip_sync_enabled = translate_file_form.cleaned_data['lip_sync_enabled']
            target_language = translate_file_form.cleaned_data['target_language']
            max_spkr=int(max_spkr)
            lip_sync_enabled = True if lip_sync_enabled == "1" else False
            print("===File: ", filename)
            print("max_spkr: ", max_spkr)
            print("lip_sync_enabled: ", lip_sync_enabled)
            print("target_language", target_language)
            root, file_extension = os.path.splitext(filename)
            file_queryset = OriginalFileModel.objects.filter(filename=filename, user=request.user)
            filename = file_queryset[0].path

            download_path = f"audio/{user.username}/{str(root)}_translate{file_extension}"
            download_path = os.path.join(file_path, download_path)
            idx = 1
            while (os.path.isfile(download_path)):
                print("saving: ", download_path)
                download_path = f"audio/{user.username}/{str(root)}_translate_{idx}{file_extension}"
                download_path = os.path.join(file_path, download_path)
                idx = idx + 1
            converted_file_model = ConvertedFileModel()
            converted_file_model.user = user
            converted_file_model.filename = os.path.basename(download_path)
            converted_file_model.path = download_path
            converted_file_model.downloadable = False
            converted_file_model.save()   

            thread = threading.Thread(
                target=transcribe, args=(lock, user, converted_file_model, filename, max_spkr, download_path, lip_sync_enabled, target_language)
            )
            thread.start()

            if not user.is_staff:
                user.trial_count -= 1
                user.save()

            return Response({
                "status": "success",
                "trial_count": user.trial_count
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)
        