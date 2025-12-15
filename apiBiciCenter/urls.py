from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from templatesApiBiciCenter import views
from django.views.generic import RedirectView
from templatesApiBiciCenter.views import (
    CarritoViewSet, 
    BicicletaViewSet, 
    RepuestoViewSet, 
    AccesorioViewSet
)


router = DefaultRouter()
router.register('bicicletas', BicicletaViewSet, basename='bicicletas')
router.register('repuestos', RepuestoViewSet, basename='repuestos')
router.register('accesorios', AccesorioViewSet, basename='accesorios')
router.register('carrito', CarritoViewSet, basename='carrito')
router.register(r'bicicletas-cliente', views.BicicletaClienteViewSet)
router.register(r'servicios-mantenimiento', views.ServicioMantenimientoViewSet)
router.register(r'ordenes-mantenimiento', views.OrdenMantenimientoViewSet)


urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/auth/login/', auth_views.obtain_auth_token),
    path('api/auth/register/', views.register_user),
    path('api/auth/logout/', views.logout_user),
    path('api/', include(router.urls)),
    path('api/usuario/', views.user_profile, name='user_profile'),
]