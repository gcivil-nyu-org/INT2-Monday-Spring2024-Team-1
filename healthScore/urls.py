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
    path("login", auth_views.LoginView.as_view(template_name="login.html", next_page="homepage"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
