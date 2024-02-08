from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("toppings/", views.toppings_editor, name="Toppings Editor"),
    path("pizza/", views.pizza_editor, name="Pizza Editor"),
]