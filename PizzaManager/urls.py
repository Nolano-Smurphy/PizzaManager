from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("toppings/", views.toppings_overview, name="Toppings Overview"),
    path("toppings/<int:topping_id>/", views.toppings_editor, name="Toppings Editor"),
    path("pizza/", views.pizza_overview, name="Pizza Overview"),
    path("pizza/<int:pizza_id>/", views.pizza_editor, name="Pizza Editor"),
]