from django.shortcuts import render

# Create your views here.


# Basic home view
def home(request):
    return render(request, 'django_notifications_app/home.html')