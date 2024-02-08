from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello World!</h1>")

def toppings_editor(request):
    return HttpResponse("<h1>Hello World! This is the Toppings Editor!</h1>")

def pizza_editor(request):
    return HttpResponse("<h1>Hello World! This is the Pizza Editor!</h1>")