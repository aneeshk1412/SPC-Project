from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt,ensure_csrf_cookie

app_name = 'user'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.userhome, name='userhome'),
    path('tree/', views.treeview, name='treeview'),
    path('<int:pk>/', views.dirview, name='dirview'),
    path('contents/<path:pth>', views.FileDetail.as_view(), name='filecontents')
    # path('contents/<path:pth>', views.file_contents, name='filecontents'),
    # path('data/<path:pth>', views.file_data, name='filedata'),
    # path('allfiles/<path:pth>', views.all_observed_files, name='allobervedfiles')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)