from django.shortcuts import render
from django.views import View
from django.http.response import JsonResponse

# Create your views here.
class LoginView(View):
    def get(request):
        return JsonResponse({ 'message': 'hello world'})