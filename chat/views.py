from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from healthConfig.settings import (
    PUSHER_APP_ID,
    PUSHER_KEY,
    PUSHER_SECRET,
    PUSHER_CLUSTER,
)
from healthScore.models import User, Hospital
from .models import ChatSession, Message
from pusher import Pusher
from django.views.decorators.csrf import csrf_exempt

pusher = Pusher(
    app_id=PUSHER_APP_ID,
    key=PUSHER_KEY,
    secret=PUSHER_SECRET,
    cluster=PUSHER_CLUSTER,
    ssl=True,
)


@login_required(login_url="/")
def get_chat_session(request, receiver_id):
    sender = request.user
    receiver = get_object_or_404(User, id=receiver_id)

    if sender.is_patient:
        # current chat and messages
        chat, created = ChatSession.objects.get_or_create(
            patient=sender, healthcareWorker=receiver
        )
        messages = chat.messages.all()
        # users that have been chatted with current user before
        receiver_ids = (
            ChatSession.objects.filter(patient_id=sender.id)
            .order_by("-createdAt")
            .values_list("healthcareWorker_id", flat=True)
            .distinct()
        )
        receivers = User.objects.filter(id__in=receiver_ids)
        receivers = list(receivers)
        receivers.sort(key=lambda receiver: list(receiver_ids).index(receiver.id))
    elif sender.is_healthcare_worker:
        # current chat and messages
        chat, created = ChatSession.objects.get_or_create(
            patient=receiver, healthcareWorker=sender
        )
        messages = chat.messages.all()
        # users that have been chatted with current user before
        receiver_ids = (
            ChatSession.objects.filter(healthcareWorker_id=sender.id)
            .order_by("-createdAt")
            .values_list("patient_id", flat=True)
            .distinct()
        )
        receivers = User.objects.filter(id__in=receiver_ids)
        receivers = list(receivers)
        receivers.sort(key=lambda receiver: list(receiver_ids).index(receiver.id))

    context = {
        "receiver_id": receiver_id,
        "receiver": receiver,
        "receivers": receivers,
        "messages": messages,
        "pusher_key": PUSHER_KEY,
    }

    return render(request, "chat/chat.html", context)


def chat_view(request):
    # get all chat sessions related to current user
    chat_log = (
        ChatSession.objects.filter(patient=request.user)
        .union(ChatSession.objects.filter(healthcareWorker=request.user))
        .order_by("-createdAt")
    )

    if chat_log.exists():
        # if it exists, load the latest chat
        first_chat = chat_log.first()
        print(first_chat.healthcareWorker.id, first_chat.patient.id)
        return redirect(
            "chat:get_chat_session",
            receiver_id=(
                first_chat.healthcareWorker.id
                if request.user == first_chat.patient
                else first_chat.patient.id
            ),
        )
    else:
        return render(request, "chat/no_chat.html")


@login_required(login_url="/")
def select_user_view(request):
    hospitals = Hospital.objects.all()
    return render(request, "chat/select_user.html", {"hospitals": hospitals})


@csrf_exempt
def pusher_authentication(request):
    channel_name = request.POST["channel_name"]
    print(channel_name)
    if channel_name.startswith(
        f"private-chat-{request.user.id}-"
    ) or channel_name.endswith(f"-{request.user.id}"):
        auth = pusher.authenticate(
            channel=channel_name, socket_id=request.POST["socket_id"]
        )
        return JsonResponse(auth)
    return JsonResponse({"message": "Forbidden"}, status=403)


def get_channel_name(author_id, other_user_id):
    if int(author_id) < int(other_user_id):
        return f"private-chat-{author_id}-{other_user_id}"
    else:
        return f"private-chat-{other_user_id}-{author_id}"


@csrf_exempt
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("message")
        author_id = request.POST.get("author_id")
        other_user_id = request.POST.get("receiver_id")

        channel_name = get_channel_name(author_id, other_user_id)

        pusher.trigger(
            channel_name,
            "new_message",
            {"author_id": author_id, "receiver_id": other_user_id, "message": content},
        )

        author = User.objects.get(id=author_id)
        other_user = User.objects.get(id=other_user_id)

        new_message = Message.objects.create(author=author, content=content)
        chat_session, created = ChatSession.objects.get_or_create(
            patient=author if author.is_patient else other_user,
            healthcareWorker=author if author.is_healthcare_worker else other_user,
        )

        chat_session.messages.add(new_message)

        return JsonResponse(
            {"status": "success", "message": "Message sent successfully"}
        )
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )
