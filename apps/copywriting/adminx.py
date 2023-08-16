import xadmin

from apps.copywriting.models import UserProductDesc, FileItem, InstagramMedia


class UserProductDescAdmin(object):
    list_display = ['product_name', 'product_type', 'description', 'result_link', 'thumb_up', 'thumb_down', 'user']
    search_fields = ['product_name', 'product_type',  'description', 'result_link', 'thumb_up', 'thumb_down', 'user']
    list_filter = ['product_name', 'product_type', 'description', 'result_link', 'thumb_up', 'thumb_down', 'user']
    model_icon = "fa fa-book"


class FileItemAdmin(object):
    list_display = ['name', 'uploaded', 'path', 'user', 'timestamp']
    search_fields = ['name', 'uploaded', 'path', 'user', 'timestamp']
    list_filter = ['name', 'uploaded', 'path', 'user', 'timestamp']
    model_icon = "fa fa-book"


class InstagramMediaAdmin(object):
    list_display = ['user', 'media_id', "url", "caption"]
    search_fields = ['user', 'media_id', "url", "caption"]
    list_filter = ['user', 'media_id', "url", "caption"]
    model_icon = "fa fa-book"


xadmin.site.register(UserProductDesc, UserProductDescAdmin)
xadmin.site.register(FileItem, FileItemAdmin)
xadmin.site.register(InstagramMedia, InstagramMediaAdmin)