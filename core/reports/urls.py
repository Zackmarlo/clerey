from django.urls import path
from .views import ASDVideosView, ASDPhysiologyView, ADHDDiagnosisView

urlpatterns = [
    # ASD: two separate pages, two separate endpoints
    path('asd/<str:child_id>/videos/', ASDVideosView.as_view()),
    path('asd/<str:child_id>/physiology/', ASDPhysiologyView.as_view()),

    # ADHD: unchanged
    path('adhd/<str:child_id>/', ADHDDiagnosisView.as_view()),
]