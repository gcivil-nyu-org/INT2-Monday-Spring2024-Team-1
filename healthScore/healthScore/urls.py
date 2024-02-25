from django.urls import path

from . import views

urlpatterns = [
    path('index', views.test_default_values, name='index'),
    path('addMockData', views.add_mock_data, name='mock_data'),
    path('view_health_history', views.view_health_history, name='view_health_history'),
    path('filter_records', views.filter_records, name='filter_records'),
]