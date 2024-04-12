from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from healthScore.models import User
from .models import ChatSession

@login_required
def chat_view(request):
    # sender = request.user
    # receiver = get_object_or_404(User, id=receiver_id)
    # ChatSession.objects.get_or_create(
    #     patient = (
    #         sender if sender.is_patient else receiver
    #     ),
    #     healthcareWorker = (
    #         sender if sender.is_healthcare_worker else receiver
    #     )
    # )
    # if sender.is_patient:
    #     ChatSession.objects.filter(patient=sender)

    return render(request, "chat/chat.html")

@login_required
def display_chat(request):
    # get all chat sessions related to current user
    chat_log = (
        ChatSession.objects.filter(patient=request.uesr)
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
    
def user_select_view(request):
    return render(request, "user_select.html")