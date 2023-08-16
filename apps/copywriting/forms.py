from django import forms

from apps.copywriting.models import InstagramMedia


class ProductDescForm(forms.Form):
    product_name = forms.CharField(required=True)
    product_type = forms.CharField(required=True)
    description = forms.CharField(required=True)


class ProductDescThumbForm(forms.Form):
    thumb = forms.CharField(required=True)
    product_desc_id = forms.FloatField(required=True)


class EditedProductDescForm(forms.Form):
    result = forms.CharField(required=True)
    product_desc_id = forms.FloatField(required=True)


class ProductDescCopyForm(forms.Form):
    product_desc_id = forms.FloatField(required=True)


class InstagramMediaForm(forms.ModelForm):
    class Meta:
        model = InstagramMedia
        fields = ["media_id", "url", "caption"]

    def clean_caption(self):
        return self.cleaned_data['caption'] or None