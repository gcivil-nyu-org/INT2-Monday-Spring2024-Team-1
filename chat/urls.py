from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_view, name="chat_view"),
    path("<int:receiver_id>", views.get_chat_session, name="get_chat_session"),
]
