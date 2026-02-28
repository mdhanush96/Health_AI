from django.urls import path
from .views import ReportUploadView, ReportAnalyzeView, ReportListView

urlpatterns = [
    path('report/upload/', ReportUploadView.as_view(), name='report-upload'),
    path('report/analyze/', ReportAnalyzeView.as_view(), name='report-analyze'),
    path('report/list/', ReportListView.as_view(), name='report-list'),
]
