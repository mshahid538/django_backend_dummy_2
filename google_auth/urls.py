


from django.urls import path
from .import views
urlpatterns = [
    path('',views.googleoauth,name='helloss'),
    path('reset/',views.reset,name='reset'),

]
