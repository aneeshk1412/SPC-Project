from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url

app_name = 'user'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.userhome, name='userhome')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
