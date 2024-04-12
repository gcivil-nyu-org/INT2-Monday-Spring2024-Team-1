from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_view, name="chat_view"),
    path("select-user", views.select_user_view, name="select_user_view")
]