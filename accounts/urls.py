from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.urls import path, include
from .views import *

app_name = 'accounts'

urlpatterns = [
                  path('', include('django.contrib.auth.urls')),
              ] + default_urlpatterns(GoogleProvider)
