from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('circle/', include('circles.urls')),
    path('', include('dashboard.urls')),
]