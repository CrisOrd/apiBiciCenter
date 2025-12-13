
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bici-center/', bici_center_view, name='bici_center'),
    path('', home_view, name='home'),
]
