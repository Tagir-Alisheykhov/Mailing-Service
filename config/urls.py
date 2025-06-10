from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.http import HttpResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('messenger/', include('messenger.urls', namespace='messenger')),
    path('users/', include('users.urls', namespace='users'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


