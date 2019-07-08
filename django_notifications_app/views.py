from django.shortcuts import render

# Create your views here.


# Basic home view
def home(request):
    return render(request, 'django_notifications_app/home.html')


from datetime import datetime

# Django Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def notification_test_page(request):

    # Django Channels Notifications Test
    current_user = request.user
    channel_layer = get_channel_layer()
    data = "notification"+ "...." + str(datetime.now())
    # Trigger message sent to group
    async_to_sync(channel_layer.group_send)(
        str(current_user.pk),  # Channel Name, Should always be string
        {
            "type": "notify",   # Custom Function written in the consumers.py
            "text": data,
        },
    )  
    return render(request, 'django_notifications_app/notifications_test_page.html')