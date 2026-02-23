from django.urls import path
from .views import ScanUploadView, ProjectHistoryView, ScanDownloadView

urlpatterns = [
    path('upload/', ScanUploadView.as_view(), name='scan-upload'),
    path('history/', ProjectHistoryView.as_view(), name='scan-history'),
    path('download-report/<int:scan_id>/', ScanDownloadView.as_view(), name='scan-download'),
]
