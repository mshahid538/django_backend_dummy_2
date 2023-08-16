import csv
import io
from datetime import datetime
import re
import requests

from requests.api import post
import threading
import base64
import hashlib
import hmac
import os
import boto3
from loguru import logger
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
import asyncio
from apps.copywriting.forms import ProductDescForm, ProductDescThumbForm, EditedProductDescForm, ProductDescCopyForm, \
    InstagramMediaForm
from apps.copywriting.models import UserProductDesc, FileItem, InstagramMedia
from apps.copywriting.serializers import UserProductDescSerializer, InstagramMediaSerializer
from apps.copywriting.utilities import autogen_prompt, execute, create_synonyms
from apps.users.models import UserProfile
from apps.users.tokens import ExpiringTokenAuthentication
from apps.copywriting.management.commands._job_list import API_ROOT
from backend.settings import (AWS_STORAGE_BUCKET_NAME,
                              AWS_ACCESS_KEY_ID,
                              AWS_SECRET_ACCESS_KEY,
                              AWS_TRANSLATE_SECRET_ACCESS_KEY,
                              AWS_TRANSLATE_ACCESS_KEY_ID,
                              AWS_S3_CUSTOM_DOMAIN,
                              FB_APP_ID,
                              FB_APP_SECRET)

import nltk
import ssl
import time
from pathlib import Path

file_path = '{}'.format(Path(__file__).resolve().parent.parent)
nltk.data.path.append(file_path)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt', download_dir=file_path)

RESPONSE_LIMITS = 4
TOTAL_RESPONSES = 10


def read_prompt_aws(filename):
    """
    Looks in aws prompts/ directory for a text file. Pass in file name only, not extension.

    Example: prompts/hello-world.txt -> read_prompt_aws('hello-world')
    """
    bytes_buffer = io.BytesIO()
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    cloudfilename = "prompts/{}.txt".format(filename)
    s3 = session.resource('s3')
    s3.Bucket(AWS_STORAGE_BUCKET_NAME).download_fileobj(
        Key=cloudfilename, Fileobj=bytes_buffer)
    return bytes_buffer.getvalue().decode()


def check_chinese(text):
    """
    Check whether there is Chinese characters in text
    Translate Chinese text to English text
    """
    if re.search(u'[\u4e00-\u9fff]', text):
        new_text = aws_translate(text)
    else:
        new_text = text
    return new_text


def aws_translate(text):
    translate = boto3.client(service_name='translate', region_name='us-west-1', use_ssl=True,
                             aws_access_key_id=AWS_TRANSLATE_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_TRANSLATE_SECRET_ACCESS_KEY)
    result = translate.translate_text(Text=text,
                                      SourceLanguageCode="zh", TargetLanguageCode="en")
    return result.get('TranslatedText')


class UserProductDescView(APIView):
    """
    View to generate result based on user's input

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
        product_form = ProductDescForm(data=request.data)
        if product_form.is_valid():
            product_name = product_form.cleaned_data["product_name"]
            product_type = product_form.cleaned_data["product_type"]
            description = product_form.cleaned_data["description"]

            if product_type == 'other':
                product_type = 'cloth'

            description = check_chinese(description)

            prompt_from_aws = read_prompt_aws('prompt_{}'.format(product_type))
            prompt_original = prompt_from_aws.format(product_name, description)
            prompt_synonym = prompt_from_aws.format(
                product_name, create_synonyms(description))

            post_result = []
            response_iterations = RESPONSE_LIMITS
            while len(post_result) < TOTAL_RESPONSES and response_iterations > 0:
                response_iterations = response_iterations - 1
                if response_iterations == RESPONSE_LIMITS - 2:
                    result = execute(autogen_prompt, prompt_synonym)
                else:
                    result = execute(autogen_prompt, prompt_original)

                # post processing returned response
                sent_tokenizer = nltk.data.load(
                    'tokenizers/punkt/english.pickle')

                for res in result:
                    processed_res = self.post_processing_text(
                        res, sent_tokenizer)
                    if processed_res != "":
                        post_result.append(processed_res)
                        if response_iterations == RESPONSE_LIMITS - 2:
                            logger.debug(f'synonym result:{result}')
            post_result = post_result[:10]
            print(f'Response_iterations: {5 - response_iterations}')
            id_array = []
            product_desc_list = []

            for _ in range(len(post_result)):
                product_desc = UserProductDesc()
                product_desc.user = request.user
                product_desc.product_name = product_name
                product_desc.description = description
                product_desc.product_type = product_type
                product_desc.save()
                id_array.append(product_desc.id)
                product_desc_list.append(product_desc)

            def save_s3(ai_post_result, ai_product_desc_list):

                session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                s3 = session.resource('s3')
                for i in range(len(ai_post_result)):
                    # Upload result to S3
                    buff = io.StringIO()
                    csvwriter = csv.writer(
                        buff, dialect='excel', delimiter=',')
                    csvwriter.writerow(
                        [request.user.get_username(), product_name, product_type, description, post_result[i],
                         datetime.now()])
                    buff2 = io.BytesIO(buff.getvalue().encode())
                    cloudfilename = "product_desc/{}/{}_{}.csv".format(request.user.get_username(), product_name,
                                                                       datetime.now().strftime("%Y%m%d_%H%M%S%f"))
                    s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
                        Key=cloudfilename, Body=buff2)

                    # Add result to database
                    product_desc = ai_product_desc_list[i]
                    product_desc.result_link = "https://{}.s3.amazonaws.com/{}".format(AWS_STORAGE_BUCKET_NAME,
                                                                                       cloudfilename)
                    product_desc.save()

            thread = threading.Thread(
                target=save_s3, args=(post_result, product_desc_list))
            thread.start()
            # Reduce trial_count by 1
            user.trial_count = user.trial_count - 1
            user_trial_count = user.trial_count
            user.save()

            return Response({
                "status": "success",
                "result": post_result,
                "product_desc_ids": id_array,
                "trial_count": user_trial_count,
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request):
        username = request.user.get_username()
        user = UserProfile.objects.get(username=username)
        # Get the latest 3 result
        product_desc = UserProductDesc.objects.filter(
            user=user).order_by('-add_time')[:3]
        all_product_desc_serial = []
        for item in product_desc:
            product_desc_serial = UserProductDescSerializer(item)
            all_product_desc_serial.append(product_desc_serial.data)

        return Response({
            "product_description": all_product_desc_serial,
        }, status=status.HTTP_200_OK)

    def post_processing_text(self, input, sent_tokenizer):
        input = input.strip()
        if len(input) < 100:
            logger.debug(
                "Returned repsonse shorter than 100 charteracters.")
            return ""

        # currently disable sent_tokenizer
        sentences = sent_tokenizer.tokenize(input)
        seen = set()
        uniq_sent = []
        for x in sentences:
            if x not in seen:
                uniq_sent.append(x)
                seen.add(x)

        # if len(uniq_sent) < 2:
        #     logger.debug(
        #         "Returned response have less than 3 sentences.")
        #     return ""
        sent_final = []
        for sent in uniq_sent:
            sent = sent[0].upper() + sent[1:]
            last_period = sent.rfind('.')
            if last_period != -1:
                sent_final.append(sent)
        sentences = " ".join(sent_final)
        return sentences


class UserProductDescThumb(APIView):
    """
    View to generate result based on user's input

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_form = ProductDescThumbForm(data=request.data)
        if product_form.is_valid():
            thumb = product_form.cleaned_data["thumb"]
            product_desc_id = product_form.cleaned_data["product_desc_id"]
            product_desc = UserProductDesc.objects.get(id=product_desc_id)
            user = request.user
            if thumb == "up":
                product_desc.thumb_up = True
                user.total_thumb_up_count += 1
            elif thumb == "down":
                product_desc.thumb_down = True
                user.total_thumb_down_count += 1

            product_desc.save()
            user.save()

            return Response({
                "status": "success",
                "msg": "Update thumb_up or thumb_down successfully",
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserProductDescCopy(APIView):
    """
    View to generate result based on user's input

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_copy_form = ProductDescCopyForm(data=request.data)
        if product_copy_form.is_valid():
            product_desc_id = product_copy_form.cleaned_data["product_desc_id"]
            product_desc = UserProductDesc.objects.get(id=product_desc_id)
            user = request.user

            product_desc.copy_desc = True
            user.total_copy_count += 1
            product_desc.save()
            user.save()
            return Response({
                "status": "success",
                "msg": "Update copy count successfully",
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserProductDescEdit(APIView):
    """
    View to generate result based on user's input

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_form = EditedProductDescForm(data=request.data)
        if product_form.is_valid():
            result = product_form.cleaned_data["result"]
            product_desc_id = product_form.cleaned_data["product_desc_id"]
            product_desc = UserProductDesc.objects.get(id=product_desc_id)

            # Upload result to S3
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3 = session.resource('s3')

            buff = io.StringIO()
            csvwriter = csv.writer(buff, dialect='excel', delimiter=',')
            csvwriter.writerow(
                [request.user.get_username(), product_desc.product_name, product_desc.product_type,
                 product_desc.description, result, datetime.now()])
            buff2 = io.BytesIO(buff.getvalue().encode())
            cloudfilename = "product_desc/{}/{}_{}.csv".format(request.user.get_username(), product_desc.product_name,
                                                               datetime.now().strftime("%Y%m%d_%H%M%S%f"))
            s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
                Key=cloudfilename, Body=buff2)

            # Add result to database
            product_desc.edited_result_link = "https://{}.s3.amazonaws.com/{}".format(AWS_STORAGE_BUCKET_NAME,
                                                                                      cloudfilename)
            product_desc.save()

            return Response({
                "status": "success",
                "msg": "Update edited copy successfully",
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class FilePolicyAPI(APIView):
    """
    This view is to get the AWS Upload Policy for our s3 bucket.
    What we do here is first create a FileItem object instance in our
    Django backend. This is to include the FileItem instance in the path
    we will use within our bucket as you'll see below.
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        The initial post request includes the filename
        and auth credientails. In our case, we'll use
        Session Authentication but any auth should work.
        """
        filename_req = request.data.get('filename')
        if not filename_req:
            return Response({"message": "A filename is required"}, status=status.HTTP_400_BAD_REQUEST)
        policy_expires = int(time.time() + 5000)
        user = request.user
        username_str = str(request.user.username)
        """
        Below we create the Django object. We'll use this
        in our upload path to AWS. 

        Example:
        To-be-uploaded file's name: Some Random File.mp4
        Eventual Path on S3: <bucket>/username/2312/2312.mp4
        """
        file_obj = FileItem.objects.create(user=user, name=filename_req)
        file_obj_id = file_obj.id
        upload_start_path = "static/media/{username}/{file_obj_id}/".format(
            username=username_str,
            file_obj_id=file_obj_id
        )
        _, file_extension = os.path.splitext(filename_req)
        filename_final = "{file_obj_id}{file_extension}".format(
            file_obj_id=file_obj_id,
            file_extension=file_extension

        )
        """
        Eventual file_upload_path includes the renamed file to the 
        Django-stored FileItem instance ID. Renaming the file is 
        done to prevent issues with user generated formatted names.
        """
        final_upload_path = "{upload_start_path}{filename_final}".format(
            upload_start_path=upload_start_path,
            filename_final=filename_final,
        )
        if filename_req and file_extension:
            """
            Save the eventual path to the Django-stored FileItem instance
            """
            file_obj.path = final_upload_path
            file_obj.save()

        policy_document_context = {
            "expire": policy_expires,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "key_name": "",
            "acl_name": "private",
            "content_name": "",
            "content_length": 524288000,
            "upload_start_path": upload_start_path,

        }
        policy_document = """
        {"expiration": "2025-01-01T00:00:00Z",
          "conditions": [ 
            {"bucket": "%(bucket_name)s"}, 
            ["starts-with", "$key", "%(upload_start_path)s"],
            {"acl": "%(acl_name)s"},

            ["starts-with", "$Content-Type", "%(content_name)s"],
            ["starts-with", "$filename", ""],
            ["content-length-range", 0, %(content_length)d]
          ]
        }
        """ % policy_document_context
        aws_secret = str.encode(AWS_SECRET_ACCESS_KEY)
        policy_document_str_encoded = str.encode(
            policy_document.replace(" ", ""))
        url = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN
        policy = base64.b64encode(policy_document_str_encoded)
        signature = base64.b64encode(
            hmac.new(aws_secret, policy, hashlib.sha1).digest())
        data = {
            "policy": policy,
            "signature": signature,
            "key": AWS_ACCESS_KEY_ID,
            "file_bucket_path": upload_start_path,
            "file_id": file_obj_id,
            "filename": filename_final,
            "url": url,
            "username": username_str,
        }
        return Response(data, status=status.HTTP_200_OK)


session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
client = session.client('s3')
resource = session.resource('s3')


class FileFinishView(APIView):
    """
    View to generate result based on user's input

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # file_id = request.POST.get('file')
        # size = request.POST.get('fileSize')
        file_id = request.data.get('file')
        size = request.data.get('fileSize')
        data = {}
        # type_ = request.POST.get('fileType')
        if file_id:
            obj = FileItem.objects.get(id=int(file_id))
            obj.size = int(size)
            obj.uploaded = True
            # obj.type = type_

            resource.Object(AWS_STORAGE_BUCKET_NAME,
                            obj.path).wait_until_exists()
            # try:
            #     response = client.put_object_acl(ACL='public-read', Bucket=AWS_STORAGE_BUCKET_NAME, Key=obj.path)
            # except client.exceptions.NoSuchKey:
            #     print("No Such Key")
            obj.path = 'https://%s/%s' % (AWS_S3_CUSTOM_DOMAIN,
                                          obj.path)
            obj.save()
            file_type = obj.path.split('.')[-1]
            data = {
                "path": obj.path,
                "type": file_type
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class InstagramMediaView(GenericAPIView):
    """
    View to generate result based on user's input

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = InstagramMediaSerializer

    def post(self, request, *args, **kwargs):
        insta_media_form = InstagramMediaForm(data=request.data)
        if insta_media_form.is_valid():
            media_id = insta_media_form.cleaned_data["media_id"]
            url = insta_media_form.cleaned_data["url"]
            caption = insta_media_form.cleaned_data["caption"]
            insta_media = InstagramMedia.objects.create(
                user=request.user, media_id=media_id, url=url, caption=caption)
            insta_media.save()

            return Response({
                "status": "success",
                "msg": "Create Instagram media successfully",
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

    def get(self, request, *args, **kwargs):
        queryset = InstagramMedia.objects.filter(user=request.user).order_by('-add_time')
        serializer = InstagramMediaSerializer(queryset, many=True)
        return self.get_paginated_response(self.paginate_queryset(serializer.data))


class LongTokenView(APIView):
    """
    Get FB long token and save to database

    * Requires token authentication.
    * Permission to a authenticated user
    """
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        fb_exchange_token = request.data.get('fb_exchange_token')
        ig_id = request.data.get("ig_id")
        long_token = ""
        user = request.user

        if fb_exchange_token and ig_id:
            response = requests.get(
                f'{API_ROOT}/oauth/access_token?grant_type=fb_exchange_token&client_id={FB_APP_ID}&client_secret={FB_APP_SECRET}&fb_exchange_token={fb_exchange_token}')
            if response.status_code == 200:
                con = response.content
                data = response.json()
                long_token = response.json()["access_token"]
                user.ig_token = long_token
                user.ig_id = ig_id
                user.save()
            else:
                print("error status code: {}".format(response.status_code))

            data = {
                "access_token": long_token,
                "expires_in": "365"
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "wrong parameters"
            }, status=status.HTTP_406_NOT_ACCEPTABLE)


class DeleteFileView(APIView):
    permission_classes = [ExpiringTokenAuthentication]
    authentication_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_id = request.POST.get('id')
        obj = FileItem.objects.get(id=int(id))

        resource.Object(AWS_STORAGE_BUCKET_NAME, obj.path).delete()
        obj.delete()

        return Response("File deleted", status=status.HTTP_200_OK)

# TODO: replace with aws
# def zh_to_en(text):
#     """
#     Translate Chinese text to English text
#     """
#     tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
#     model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
#     tokenized_text = tokenizer.prepare_seq2seq_batch([text], return_tensors='pt')
#     translation = model.generate(**tokenized_text)
#     translated_text = tokenizer.batch_decode(translation, skip_special_tokens=False)[0]
#     return translated_text
#
#


# def sagemaker_zh_to_en(text):
#     arn = 'arn:aws:iam::563884117207:role/sageMakerRole'
#
#     # TODO: Create aws key for sagemaker
#     iam = boto3.client('iam',
#                        aws_access_key_id=AWS_ACCESS_KEY_ID,
#                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
#                        )
#     role = iam.get_role(RoleName='sageMakerRole')['Role']['Arn']
#     print(role)
#
#     policy = iam.get_policy(
#         PolicyArn=arn
#     )
#     print(policy)
#     policy_version = iam.get_policy_version(
#         PolicyArn=arn,
#         VersionId=policy['Policy']['DefaultVersionId']
#     )
#
#     print(json.dumps(policy_version['PolicyVersion']['Document']))
#     print(json.dumps(policy_version['PolicyVersion']['Document']['Statement']))
