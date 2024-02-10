from django.shortcuts import render
from django.http import HttpResponse

from .models import Topping, Pizza

# Create your views here.
def index(request):
    return HttpResponse(render(request, "PizzaManager/landing_page.html"))

def toppings_overview(request):
    toppings_list = Topping.objects.order_by("name")[:5]
    context = {"toppings_list": toppings_list}
    return HttpResponse(render(request, "PizzaManager/toppings_overview.html", context))

def toppings_editor(request, topping_id):
    final_response = "<h1>Hello World! This is the Toppings Editor!</h1><br>"
    final_response = final_response + "You are currently looking at the <b>%s</b> topping."
    return HttpResponse(final_response % topping_id)

def pizza_overview(request):
    pizzas_list = Pizza.objects.order_by("name")[:5]
    context = {"pizzas_list": pizzas_list}
    return HttpResponse(render(request, "PizzaManager/pizza_overview.html", context))

def pizza_editor(request, pizza_id):
    final_response = "<h1>Hello World! This is the Pizza Editor!</h1><br>"
    final_response = final_response + "You are currently looking at the <b>%s</b> pizza."
    return HttpResponse(final_response % pizza_id)