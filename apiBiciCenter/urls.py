from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from templatesApiBiciCenter import views

router = DefaultRouter()
router.register(r'bicicletas', views.BicicletaViewSet)
router.register(r'repuestos', views.RepuestoViewSet)
router.register(r'accesorios', views.AccesorioViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', auth_views.obtain_auth_token),
    path('api/', include(router.urls)),
]