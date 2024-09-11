from django import forms


class ChatForm(forms.Form):
    chat_message = forms.CharField(label="Your Message", max_length=100)