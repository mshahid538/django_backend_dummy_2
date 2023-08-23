


from django.urls import path
from .import views
urlpatterns = [
    path('',views.googleoauth,name='helloss'),
    path('reset/',views.reset,name='reset'),
    path('delete/',views.remove,name='remove'),
    path('edit_name/',views.reset_name,name='reset_name'),
    path('edit_email/',views.reset_email,name='reset_email'),

]
