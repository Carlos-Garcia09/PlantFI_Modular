from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from app import views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('analisis/', views.analisis, name='analisis'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('add_plant/', views.add_plant, name='add_plant'),
    path('mi_jardin/', views.mi_jardin, name='mi_jardin'),
    path('eliminar_bitacora/<int:id_bitacora>/', views.eliminar_bitacora, name='eliminar_bitacora'),

    path('bitacora_planta/<int:planta_id>/', views.bitacora_planta, name='bitacora_planta'),
    path('mi_jardin/detalle_planta/<int:id_planta>/', views.detalle_planta, name='detalle_planta'),
    path('eliminar_planta/<int:id_planta>/', views.eliminar_planta, name='eliminar_planta'),
    path('login-with-google/', views.login_with_google, name='login_with_google'),
    path('complete/google-oauth2/', views.complete_google_auth, name='complete_google_auth'),
    path('social-auth/', include('social_django.urls', namespace='social')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
