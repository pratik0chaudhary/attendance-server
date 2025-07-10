from django.urls import path

from .admin import admin_site

app_name = 'attendance'
urlpatterns = [
    path('', admin_site.urls),
]
