from django.contrib import admin

from apps.copywriting.models import UserProductDesc


class UserProductDescxAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserProductDesc, UserProductDescxAdmin)
