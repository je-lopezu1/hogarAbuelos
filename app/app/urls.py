from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('accounts/', include('authentication.urls', namespace='authentication')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('residents/', include('residents.urls', namespace='residents')),
    path('medications/', include('medications.urls', namespace='medications')),
    path('medication_dose/', include('medication_dose.urls', namespace='medication_dose')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)