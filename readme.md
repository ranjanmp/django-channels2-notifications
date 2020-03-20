# Django Notifications Using Channels 2

Django Channels is a project that takes Django and extends its abilities beyond HTTP, to handle WebSockets, chat protocols, IoT protocols, and more. It’s built on a Python specification called ASGI. Django Channels has been updated to version 2 and has a lot of improvements from the previous version. 

This Article shows how to send realtime notifications to logged in users with Django Channels 2.

## Prerequisites

A Django Project already up and Running

## Installation

1. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install django-channels.

```bash
pip install django-channels
```
Add 'channels' to the installed apps


2. Install channels-redis
```bash
pip install channels-redis
```

3. Install Redis and run the redis server

## in settings.py



```python
# Django Channels
ASGI_APPLICATION = "django_notifications_project.routing.application"    # your_project_name.routing.application
# End Django Channels
```

```python
# Django Channels
# Adding Django Channel Layers

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],   # Change localhost to the ip in which you have redis server running on.
        },
    },
}

# End Django Channels
```

## Create asgi.py in django project folder (In the Folder containing settings.py)

### in asgi.py

```python
"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_notifications_project.settings") #  your_project_name.settings
django.setup()
application = get_default_application()
```


## Create consumers.py in django application folder (In the Folder containing views.py)

### in consumers.py

```python
from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync


class NotificationConsumer(WebsocketConsumer):
    
    # Function to connect to the websocket
    def connect(self):
       # Checking if the User is logged in
        if self.scope["user"].is_anonymous:
            # Reject the connection
            self.close()
        else:
            # print(self.scope["user"])   # Can access logged in user details by using self.scope.user, Can only be used if AuthMiddlewareStack is used in the routing.py
            self.group_name = str(self.scope["user"].pk)  # Setting the group name as the pk of the user primary key as it is unique to each user. The group name is used to communicate with the user.
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
            self.accept()

    # Function to disconnet the Socket
    def disconnect(self, close_code):
        self.close()
        # pass

    # Custom Notify Function which can be called from Views or api to send message to the frontend
    def notify(self, event):
        self.send(text_data=json.dumps(event["text"]))
```

## Create routing.py in django project folder (In the Folder containing settings.py)

### in routing.py

```python
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from django_notifications_app.consumers import NotificationConsumer  # Importing notification Consumer from consumers.py

application = ProtocolTypeRouter({ 
    # Websocket chat handler
    'websocket': AllowedHostsOriginValidator(  # Only allow socket connections from the Allowed hosts in the settings.py file
        AuthMiddlewareStack(  # Session Authentication, required to use if we want to access the user details in the consumer 
            URLRouter(
                [
                    path("notifications/", NotificationConsumer),    # Url path for connecting to the websocket to send notifications.
                ]
            )
        ),
    ),
})
```

### Connect to Websocket
Add the below code in the template file (html) file, to connect to the websocket. Preferabally add this to the base.html and extend base.html in the other templates.

```javascript

<script>
    var loc = window.location
    var wsStart = "ws://"
    if (loc.protocol == "https:"){
        wsStart = "wss://"
    }
    var webSocketEndpoint =  wsStart + loc.host + '/notifications/'  // ws : wss   // Websocket URL, Same on as mentioned in the routing.py


    var socket = new WebSocket(webSocketEndpoint) // Creating a new Web Socket Connection

    // Socket On receive message Functionality
    socket.onmessage = function(e){
        console.log('message', e)
        console.log(e.data) // Access the notification data
        //$("body").append("<h3>"+e.data+"</h3>")
        // Can write any functionality based on your requirement
    }

    // Socket Connet Functionality
    socket.onopen = function(e){
        console.log('open', e)
    }

    // Socket Error Functionality
    socket.onerror = function(e){
        console.log('error', e)
    }

    // Socket close Functionality
    socket.onclose = function(e){
        console.log('closed', e)
    }
</script>
```


### Send notification through websocket

```python
# Django Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
```

Use the below code to send notification (data) to the frontend. 
```python
current_user = request.user # Getting current user
channel_layer = get_channel_layer()
data = "notification"+ "...." + str(datetime.now()) # Pass any data based on your requirement
# Trigger message sent to group
async_to_sync(channel_layer.group_send)(
    str(current_user.pk),  # Group Name, Should always be string
    {
        "type": "notify",   # Custom Function written in the consumers.py
        "text": data,
    },
)  

```

In this project, when the user logs in, a group is created in with the group name as the user's primary key. The notifications are sent to the respective group. The notifications are sent to the respective group of which the user is part of.


## Contributing
Pull requests are welcome. For major changes or if you have any questions, please open an issue first to discuss what you would like to change or ask.


## License
[MIT](https://choosealicense.com/licenses/mit/)
