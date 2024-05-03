"""
URL configuration for virtual_graffiti_box project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from . import views, settings, api
from django.conf.urls.static import static

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('', views.admin_panel, name='admin_panel'),
    path('settings/<str:user_identifier>/<int:code>/', views.settings, name='settings'),
    path('api/v1/fetch_settings_url/<int:code>/', api.fetch_settings_url, name='fetch_settings_url'),
    path('api/v1/validate_code/<int:code>/', api.validate_code, name='validate_code'),
    path('set_laser_color/<str:laser_id>/<int:code>/', views.set_laser_color, name='set_laser_color'),
    path('set_laser_size/<str:laser_id>/<int:code>/', views.set_laser_size, name='set_laser_size'),
    path('get_laser/<str:laser_id>/<int:code>/', views.get_laser, name='get_laser'),
    re_path(r'^.*/$', views.errors, name='errors'),
]


if settings.DEBUG:
    urlpatterns += [path('admin/', admin.site.urls)]
# else:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
