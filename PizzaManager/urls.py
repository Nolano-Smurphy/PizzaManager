from django.urls import path

from . import views

app_name = "PizzaManager"
urlpatterns = [
    path("", views.index, name="index"),
    path("toppings/", views.ToppingsOverview.as_view(), name="Toppings Overview"),
    path("toppings/<int:topping_id>/", views.toppings_editor, name="Toppings Editor"),
    path("toppings/new", views.topping_create, name="Topping Create"),
    path("pizza/", views.PizzaOverview.as_view(), name="Pizza Overview"),
    path("pizza/<int:pizza_id>/", views.pizza_editor, name="Pizza Editor"),
    path("pizza/new", views.pizza_create, name="Pizza Create"),
]