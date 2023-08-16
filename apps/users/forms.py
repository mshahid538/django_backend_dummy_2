from django import forms

from apps.users.models import UserProfile


class ChangePwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)

    def clean(self):
        pwd1 = self.cleaned_data["password1"]
        pwd2 = self.cleaned_data["password2"]

        if pwd1 != pwd2:
            raise forms.ValidationError("密码不一致")
        return self.cleaned_data


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "email"]


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["image"]


class UserPricingTierForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["trial_count", "pricing_tier"]


class RegisterPostForm(forms.Form):
    # mobile = forms.CharField(required=True, min_length=11, max_length=11)
    # code = forms.CharField(required=True, min_length=4, max_length=4)
    username = forms.CharField(required=True, min_length=1, max_length=20)
    email = forms.CharField(required=True)
    password = forms.CharField(required=True)

    def clean_username(self):
        username = self.data.get("username")
        users = UserProfile.objects.filter(username=username)
        if users:
            raise forms.ValidationError("Username is used!")
        return username

    def clean_email(self):
        email = self.data.get("email")
        users = UserProfile.objects.filter(email=email)
        if users:
            raise forms.ValidationError("Email is used!")
        return email


class LoginForm(forms.Form):
    username = forms.CharField(required=True, min_length=2)
    password = forms.CharField(required=True, min_length=3)


class ContactForm(forms.Form):
    name = forms.CharField(required=True, min_length=1)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea)


class ActivateForm(forms.Form):
    uid = forms.CharField(required=True, min_length=2)
    token = forms.CharField(required=True, min_length=2)


class InstagramForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["ig_id", "ig_token"]
