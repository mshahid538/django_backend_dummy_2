import xadmin

from apps.chat.models import UserInputText, OriginalFileModel, ConvertedFileModel


class UserInputTextAdmin(object):
    list_display = ['input_text', 'user']
    search_fields = ['input_text', 'user']
    list_filter = ['input_text', 'user']
    model_icon = "fa fa-book"

class OriginalFileModelAdmin(object):
    list_display = ['filename', 'path', 'user']
    search_fields = ['filename', 'path', 'user']
    list_filter = ['filename', 'path', 'user']
    model_icon = "fa fa-book"

class ConvertedFileModelAdmin(object):
    list_display = ['filename', 'path', 'user']
    search_fields = ['filename', 'path', 'user']
    list_filter = ['filename', 'path', 'user']
    model_icon = "fa fa-book"


xadmin.site.register(UserInputText, UserInputTextAdmin)
xadmin.site.register(OriginalFileModel, OriginalFileModelAdmin)
xadmin.site.register(ConvertedFileModel, ConvertedFileModelAdmin)