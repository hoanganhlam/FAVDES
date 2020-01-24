"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^v1/activity/', include(('apps.activity.api.urls', 'api_activity'), namespace='api_activity')),
    url(r'^v1/auth/', include(('apps.authentication.api.urls', 'api_auth'))),
    url(r'^v1/destination/', include(('apps.destination.api.urls', 'api_destination'), namespace='api_destination')),
    url(r'^v1/worker/', include(('apps.worker.api.urls', 'api_worker'), namespace='api_worker')),
    url(r'^v1/media/', include(('apps.media.api.urls', 'api_media'), namespace='api_media')),
]
