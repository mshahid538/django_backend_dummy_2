from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from apps.users.views import UserView

router = DefaultRouter()
router.register('', UserView)

urlpatterns = [
    path('', include(router.urls)),
]
