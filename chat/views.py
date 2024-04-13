from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from healthScore.models import User
from .models import ChatSession, Message

@login_required
def chat_view(request, receiver_id):
    sender = request.user
    receiver = get_object_or_404(User, id=receiver_id)

    if sender.is_patient:
        patient = sender
        healthcare_worker = receiver
        # users that have been chatted with current user before
        receiver_ids = (
            ChatSession.objects.filter(patient_id=sender.id)
            .values_list("healthcareWorker_id", flat=True).distinct()
        )
        receivers = User.objects.filter(id__in=receiver_ids)
        # current chat and messages
        chat = ChatSession.objects.get_or_create(patient=sender, healthcareWorker=receiver)
        messages = chat.messages.all()
    elif sender.is_healthcare_worker:
        patient = receiver
        healthcare_worker = sender
        # users that have been chatted with current user before
        receiver_ids = (
            ChatSession.objects.filter(healthcareWorker_id=sender.id)
            .values_list("patient_id", flat=True).distinct()
        )
        receivers = User.objects.filter(id__in=receiver_ids)
        # current chat and messages
        chat = ChatSession.objects.get_or_create(patient=receiver, healthcareWorker=sender)
        messages = chat.messages.all()


    context = {
        "patient": patient,
        "healthcare_worker": healthcare_worker,
        "chatted_users": receivers,
        "messages": messages,
        "receiver_id": str(receiver_id)
    }

    return render(request, "chat/chat.html", context)

@login_required
def initial_chat_view(request):
    # get all chat sessions related to current user
    chat_log = (
        ChatSession.objects.filter(patient=request.user)
        .union(ChatSession.objects.filter(healthcareWorker=request.user))
        .order_by("-createdAt")
    )

    if chat_log.exists():
        # if it exists, load the latest chat
        first_chat = chat_log.first()
        return redirect('chat:chat_view', receiver_id=(
            first_chat.healthcareWorker.id
            if request.user == first_chat.patient 
            else first_chat.patient.id
            )
        )
    else:
        return render(request, "chat/no_chat.html")

@login_required   
def select_user_view(request):
    return render(request, "chat/select_user.html")