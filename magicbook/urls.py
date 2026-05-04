"""Root URL configuration for MagicBook."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import HomeView

urlpatterns = [
    # Admin site, public home and app route mounts.
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
]

if settings.DEBUG:
    # In development, serve media files directly through Django.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
