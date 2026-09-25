from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.TaraqqiyLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register_choice, name="register_choice"),
    path("register/student/", views.student_signup, name="student_signup"),
    path("register/center/", views.center_signup, name="center_signup"),
    path("dashboard/", views.choose_dashboard, name="choose_dashboard"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/test/<str:subject_code>/", views.start_test, name="start_test"),
    path("student/test/submit/<int:attempt_id>/", views.submit_test, name="submit_test"),
    path("student/test/result/<int:attempt_id>/", views.test_result, name="test_result"),
    path("center/", views.center_dashboard, name="center_dashboard"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
]
