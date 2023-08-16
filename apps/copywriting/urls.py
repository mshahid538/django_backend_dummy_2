from django.conf.urls import url

from apps.copywriting.views import UserProductDescView, UserProductDescThumb, UserProductDescCopy, UserProductDescEdit, \
    InstagramMediaView, LongTokenView

urlpatterns = [
    url(r'^product_desc/$', UserProductDescView.as_view(), name="product_desc"),
    url(r'^product_desc_thumb/$', UserProductDescThumb.as_view(), name="product_desc_thumb"),
    url(r'^product_desc_copy/$', UserProductDescCopy.as_view(), name="product_desc_copy"),
    url(r'^product_desc_edit/$', UserProductDescEdit.as_view(), name="product_desc_edit"),
    url(r'^instagram_media/$', InstagramMediaView.as_view(), name="instagram_media"),
    url(r'^get_long_token/$', LongTokenView.as_view(), name="get_long_token"),
]
