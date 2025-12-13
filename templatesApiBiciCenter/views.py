from django.shortcuts import render
from django.http import JsonResponse

def bici_center_view(request):
    data = {
        'message': 'Welcome to the Bici Center API!',
        'status': 'success'
    }
    return JsonResponse(data)

def home_view(request):
    return render(request, 'home.html')