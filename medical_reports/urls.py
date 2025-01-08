from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from reports.views import signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='reports/home.html'), name='home'),
    path('reports/', include('reports.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
