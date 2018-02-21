"""demo_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView

from my_app.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$',
        TemplateView.as_view(template_name='home.html'), name='home'),
    url(
        regex=r'^mydata$',
        view=HomeView.as_view(),
        name='mydata'
     ),
    url(r'^accounts/', include('allauth.urls')),
    # url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    # url(settings.ADMIN_URL, admin.site.urls),


]  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     # This allows the error pages to be debugged during development, just visit
#     # these url in browser to see how these error pages look like.
#     urlpatterns += [
#         url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
#         url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
#         url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
#         url(r'^500/$', default_views.server_error),
#     ]
#     if 'debug_toolbar' in settings.INSTALLED_APPS:
#         import debug_toolbar
#         urlpatterns = [
#             url(r'^__debug__/', include(debug_toolbar.urls)),
#         ] + urlpatterns
