from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from healthScore.models import User, Hospital
from .models import ChatSession, Message
from django.http import JsonResponse

@login_required
def get_chat_session(request, receiver_id):
    sender = request.user
    receiver = get_object_or_404(User, id=receiver_id)

    if sender.is_patient:
        # users that have been chatted with current user before
        receiver_ids = (
            ChatSession.objects.filter(patient_id=sender.id)
            .values_list("healthcareWorker_id", flat=True).distinct()
        )
        receivers = User.objects.filter(id__in=receiver_ids)
        # current chat and messages
        chat, created = ChatSession.objects.get_or_create(patient=sender, healthcareWorker=receiver)
        messages = chat.messages.all()
    elif sender.is_healthcare_worker:
        # users that have been chatted with current user before
        receiver_ids = (
            ChatSession.objects.filter(healthcareWorker_id=sender.id)
            .values_list("patient_id", flat=True).distinct()
        )
        receivers = User.objects.filter(id__in=receiver_ids)
        # current chat and messages
        chat, created = ChatSession.objects.get_or_create(patient=receiver, healthcareWorker=sender)
        messages = chat.messages.all()


    context = {
        "receiver_id": receiver_id,
        "receiver": receiver,
        "receivers": receivers,
        "messages": messages,
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
        return redirect('chat:get_chat_session', receiver_id=(
            first_chat.healthcareWorker.id
            if request.user == first_chat.patient 
            else first_chat.patient.id
            )
        )
    else:
        return render(request, "chat/no_chat.html")

@login_required   
def select_user_view(request):
    hospitals = Hospital.objects.all()
    return render(request, "chat/select_user.html", {'hospitals':hospitals})

def get_receiver_list(request):
    if request.user.is_patient:
        receiver_ids = ChatSession.objects.filter(patient=request.user).order_by("-createdAt").values_list("healthcareWorker_id", flat=True).distinct()
        receivers = list(User.objects.filter(id__in=receiver_ids).values())
    elif request.user.is_healthcareWorker:
        receiver_ids = ChatSession.objects.filter(healthcareWorker=request.user).order_by("-createdAt").values_list("patient_id", flat=True).distinct()
        receivers = list(User.objects.filter(id__in=receiver_ids).values())
    return JsonResponse({'receivers': receivers})