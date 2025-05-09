from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('Guest.urls')),  # Include URLs from the 'user' app
    path('', include('hotal_manager.urls')),  # Include URLs from the 'hotel_manager' app'
]
