from django.urls import path
from .views import ScanUploadView, ProjectHistoryView

urlpatterns = [
    path('upload/', ScanUploadView.as_view(), name='scan-upload'),
    path('history/', ProjectHistoryView.as_view(), name='scan-history'),
]
