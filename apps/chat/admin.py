from django.contrib import admin

from apps.chat.models import UserInputText


class UserInputTextxAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserInputText, UserInputTextxAdmin)
