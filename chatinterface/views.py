from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime

from chatinterface.forms import ChatForm

from .models import ChatMessage

@login_required
def index(request):
    messages = ChatMessage.objects.order_by("created_at")

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            print("received", form.cleaned_data)
            message_text = form.cleaned_data.get("chat_message", "")
            message = ChatMessage(content=message_text, author=request.user, created_at=datetime.now())
            message.save()
        else:
            print(form.errors)
    else: 
        form = ChatForm()

    context = { "chat_messages": messages, "form": form}
    return render(request, "chatinterface/index.html", context)


