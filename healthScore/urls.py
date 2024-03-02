from django.urls import path

from . import views

urlpatterns = [
    path("homepage", views.homepage, name="homepage"),
    path("index", views.test_default_values, name="index"),
    path("addMockData", views.add_mock_data, name="mock_data"),
    path("registration", views.register, name="register"),
    path("viewHealthHistory", views.view_health_history, name="view_health_history"),
]
