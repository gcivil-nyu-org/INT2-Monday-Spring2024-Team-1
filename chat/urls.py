from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_view, name="chat_view"),
    path("<int:receiver_id>/", views.get_chat_session, name="get_chat_session"),
    path("select-user", views.select_user_view, name="select_user_view"),
    path("pusher/auth/", views.pusher_authentication, name="pusher_authentication"),
    path("send-message/", views.send_message, name="send_message"),
]
