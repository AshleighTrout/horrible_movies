from django.shortcuts import render
from django.http import HttpResponse

def inventory(request):
    return HttpResponse("Hit inventory endpoint")