from django.conf.urls import url

from apps.chat.views import UserInputTextView, UploadFileView, DownloadFileView, DeleteFileView, UploadedFileTranslateView

urlpatterns = [
    url(r'^input_text/$', UserInputTextView.as_view(), name="input_text"),
    url(r'^upload_file/$', UploadFileView.as_view(), name="upload_file"),
    url(r'^download_file/$', DownloadFileView.as_view(), name="download_file"),
    url(r'^download_file/(?P<file_type>[\w]+)/$', DownloadFileView.as_view(), name="download_file"),
    url(r'^delete_file/$', DeleteFileView.as_view(), name="delete_file"),
     url(r'^translate_file/$', UploadedFileTranslateView.as_view(), name="translate_file"),
]
