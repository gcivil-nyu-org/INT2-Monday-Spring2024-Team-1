from django.urls import path

from . import views

urlpatterns = [
    path('index', views.test_default_values, name='index')
]