from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("homepage", views.homepage, name="homepage"),
    path("index", views.test_default_values, name="index"),
    path("addMockData", views.add_mock_data, name="mock_data"),
    path("registration", views.registration, name="registration"),
    path("viewHealthHistory", views.view_health_history, name="view_health_history"),
    path("viewReports", views.view_report, name="view_reports"),

    path("login", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("viewRequests", views.view_health_history_requests, name="view_requests"),

    path("password-reset", 
         auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
         name="password_reset"),
    path("password-reset-sent", 
         auth_views.PasswordResetDoneView.as_view(),
         name="password_reset_sent"),
    path("password-change", auth_views.PasswordChangeView.as_view()),
    path("password-change-done", auth_views.PasswordChangeDoneView.as_view())
]
