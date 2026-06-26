from django.urls import path
from .views import (
    ChildProfileListCreateView,
    ChildProfileDetailView,
    DoctorAccessView,
    ClinicNoteView,
    RegenerateChildPasswordView,
    LoggedInDoctorListView,
    SendChildAccessToDoctorView,
)

urlpatterns = [
    path('', ChildProfileListCreateView.as_view()),
    path('access/', DoctorAccessView.as_view()),
    path('loggedin-doctors/', LoggedInDoctorListView.as_view()),
    path('<str:child_id>/send-access/', SendChildAccessToDoctorView.as_view()),
    path('<str:child_id>/regenerate-password/', RegenerateChildPasswordView.as_view()),
    path('<str:child_id>/', ChildProfileDetailView.as_view()),
    path('<str:child_id>/clinic-note/', ClinicNoteView.as_view()),
]