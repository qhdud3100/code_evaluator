from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from django.urls import path, include

from accounts.views import UserUpdate

app_name = 'accounts'

urlpatterns = [
                  path('', include('django.contrib.auth.urls')),
                  path('profile/', UserUpdate.as_view(), name='user_update')
              ] + default_urlpatterns(GoogleProvider)
