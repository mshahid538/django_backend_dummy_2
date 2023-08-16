from django import forms

class UserInputTextForm(forms.Form):
    user_input_text = forms.CharField(required=True)

class UploadFileForm(forms.Form):
    file = forms.FileField(required=True)
    num_speaker = forms.CharField(required=True)
    lip_sync_enabled = forms.CharField(required=True)
    target_language = forms.CharField(required=True)

class TranslateFileForm(forms.Form):
    filename = forms.CharField(required=True)
    num_speaker = forms.CharField(required=True)
    lip_sync_enabled = forms.CharField(required=True)
    target_language = forms.CharField(required=True)
    

class DownloadFileForm(forms.Form):
    filename = forms.CharField(required=True)
    is_original = forms.CharField(required=True)