from django.contrib import admin
from django.urls import path, include
from django.urls import re_path as url
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', include('centuryproperties.apps.realestates.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)