from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('Guest.urls')),  # Include URLs from the 'user' app
    path('', include('hotal_manager.urls')),  # Include URLs from the 'hotel_manager' app'

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
