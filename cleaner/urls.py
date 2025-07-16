from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

#app_name = 'cleaner'

urlpatterns = [
    path('', views.upload_view, name='upload_view'),
    path('analyze/<uuid:file_id>/', views.analyze_view, name='analyze_view'),
    path('process/<uuid:job_id>/', views.process_view, name='process_view'),
    path('results/<uuid:job_id>/', views.results_view, name='results_view'),
    path('download/<uuid:job_id>/<str:file_type>/', views.download_file, name='download_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
