from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("homepage", views.homepage, name="homepage"),
    path("addMockData", views.add_mock_data, name="mock_data"),
    path("registration", views.registration, name="registration"),
    path("viewHealthHistory", views.view_health_history, name="view_health_history"),
    path("viewReports", views.view_report, name="view_reports"),
    path("login", views.login_view, name="login"),
    path("userInfo", views.view_user_info, name="user_info"),
    path("viewRequests", views.view_health_history_requests, name="view_requests"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("editUserInfo", views.edit_user_info, name="edit_user_info"),
]
