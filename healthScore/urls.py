from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("homepage", views.homepage, name="homepage"),
    path("registration/", views.registration, name="registration"),
    path("login/", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset-done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("editUserInfo", views.edit_user_info, name="edit_user_info"),
    path("userInfo", views.view_user_info, name="user_info"),
    path("viewRequests", views.view_health_history_requests, name="view_requests"),
    path("viewHealthHistory", views.view_health_history, name="view_health_history"),
    path("viewReports", views.view_report, name="view_reports"),

    path("<int:id>/edit/", views.edit_health_record_view, name="edit_health_record"),
    path("new/", views.add_health_record_view, name="new_health_record"),
    path("record-sent/", views.record_sent_view, name="new_health_record_sent"),
]
