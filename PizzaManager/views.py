from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

import logging

from .models import Topping, Pizza

# Create your views here.
def index(request):
    """
    This view serves as the homepage for the site and asks if the user is either an Owner or a Chef.
    """
    return HttpResponse(render(request, "PizzaManager/landing_page.html"))

class ToppingsOverview(generic.ListView):
    """
    This is the view responsible for providing a list of all available toppings to the Owner.
    """
    template_name = "PizzaManager/toppings_overview.html"
    context_object_name = "toppings_list"
    paginate_by = 10

    def get_queryset(self):
        return Topping.objects.all().order_by("name")

def toppings_editor(request, topping_id):
    """
    This is the view responsible for handling all changes that might need to occur to a topping.
    """
    topping = get_object_or_404(Topping, pk=topping_id)
    return render(request, "PizzaManager/toppings_editor.html", {"topping": topping})

class PizzaOverview(generic.ListView):
    """
    This is the view responsible for providing a list of all available pizzas to the Chef.
    """
    template_name = "PizzaManager/pizza_overview.html"
    context_object_name = "pizzas_list"
    paginate_by = 5

    def get_queryset(self):
        return Pizza.objects.all().order_by("name")

def pizza_editor(request, pizza_id):
    """
    This is the view responsible for handling all changes that might need to occur to a pizza.
    """
    pizza = get_object_or_404(Pizza, pk=pizza_id)

    #Guard statement to ensure GET requests can be processed quickly.
    if request.method =='GET':
        return render(request, "PizzaManager/pizza_editor.html", {"pizza": pizza})
    
    # Requests, by this point, should be exclusively POST requests and will take time to process.
    try:
        # Process name changes
        if "pizza_name_change" in request.POST:
            new_name = request.POST["new_name"]
            # Check if the new name is an empty string or composed of all white space.
            if new_name.strip() != "":
                # Check for special characters.
                if not hasSpecialChar(new_name):
                    # Check for any duplicate entries that already exist.
                    if not any(new_name == object.name for object in Pizza.objects.all()):
                        pizza.name = new_name
                        pizza.save()
                    else:
                        return pizzaErrorReply(
                            request,
                            pizza,
                            destination="PizzaManager/pizza_editor.html",
                            error_message="A pizza with this name already exists. Please enter a unique name. Name unchanged."
                        )

                else:
                    return pizzaErrorReply(
                        request,
                        pizza,
                        destination="PizzaManager/pizza_editor.html",
                        error_message="Please do not include any special characters in the pizza name. Name unchanged."
                    )
            else:
                return pizzaErrorReply(
                    request,
                    pizza,
                    destination="PizzaManager/pizza_editor.html",
                    error_message="Received blank. Name unchanged."
                )

        # Process pizza deletions
        elif "pizza_delete" in request.POST:
            pizza.delete()
            return HttpResponseRedirect(reverse("PizzaManager:Pizza Overview"))
        
        # Process topping changes
        elif "pizza_topping_change" in request.POST:
            return pizzaErrorReply(
                request,
                pizza,
                destination="PizzaManager/pizza_editor.html",
                error_message="This feature has not been implemented yet."
            )
        
        # Process topping removals
        elif "pizza_topping_delete" in request.POST:
            return pizzaErrorReply(
                request,
                pizza,
                destination="PizzaManager/pizza_editor.html",
                error_message="This feature has not been implemented yet."
            )

    # Should never occur on production if I did this right.
    except(KeyError):
        logging.exception(KeyError.__traceback__)
        return pizzaErrorReply(
                request,
                pizza,
                destination="PizzaManager/pizza_editor.html",
                error_message="Internal Error occurred. Contact Nolan Murphy about resolving this."
            )
    
    except (Pizza.DoesNotExist):
        return pizzaErrorReply(
                request,
                pizza,
                destination="PizzaManager/pizza_editor.html",
                error_message="You have attempted to alter a pizza that does not exist."
            )
    
    except (Topping.DoesNotExist):
        return pizzaErrorReply(
                request,
                pizza,
                destination="PizzaManager/pizza_editor.html",
                error_message="You have attempted to alter a topping that does not exist."
            )
    
    # Exceptions hopefully won't occur, but it's better to be prepared.
    else:
        return HttpResponseRedirect(reverse("PizzaManager:Pizza Editor", args=(pizza.id,)))
    
def pizza_create(request):

    toppings_list = Topping.objects.all()

    if request.method =='GET':
        context = {"toppings_list": toppings_list}
        return render(request, "PizzaManager/pizza_new.html", context)

    # Process POST requests
    try:
        if "pizza_new" in request.POST:
            pizza_name = request.POST["new_pizza_name"]
            if pizza_name.strip() != "":
                if not hasSpecialChar(pizza_name):
                    if not any(pizza_name == object.name for object in Pizza.objects.all()):
                        new_pizza = Pizza(name=pizza_name)
                        new_pizza.save()
                        for topping in request.POST.getlist("toppings_options"):
                            logging.warning("Adding %s to a pizza." % topping)
                            topping_to_add = Topping.objects.get(name=topping)
                            new_pizza.toppings.add(topping_to_add)
                        new_pizza.save()
                        return HttpResponseRedirect(reverse("PizzaManager:Pizza Overview"))
                    else:
                        return createPizzaErrorReply(
                            request, 
                            toppings_list, 
                            destination="PizzaManager/pizza_new.html",
                            error_message="A pizza with this name already exists. Please enter a unique name. No pizza created."
                        )
                else:
                    return createPizzaErrorReply(
                        request, 
                        toppings_list, 
                        destination="PizzaManager/pizza_new.html",
                        error_message="Please do not include any special characters in the pizza name. No pizza created."
                    )
            else:
                return createPizzaErrorReply(
                    request, 
                    toppings_list, 
                    destination="PizzaManager/pizza_new.html",
                    error_message="Received blank. No pizza created."
                )
        elif "cancel_pizza_new" in request.POST:
            return HttpResponseRedirect(reverse("PizzaManager:Pizza Overview"))

    except (KeyError):
        return createPizzaErrorReply(
            request,
            toppings_list,
            destination="PizzaManager/pizza_new.html",
            error_message="Internal Error occurred. Contact Nolan Murphy about resolving this."
        )

def hasSpecialChar(data_to_validate : str) -> bool:
    """
    Helper method to make sure the string passed in contains only alpha-numeric characters (blank spaces are permissible).
    @param data_to_validate: String to be evaluated for special characters.
    @return `True` if a special character is found. Otherwise returns `False`.
    """
    
    for char in data_to_validate:
        if not (char.isalnum() or char.isspace()):
            return True

    return False

def pizzaErrorReply(request, pizza, destination : str, error_message : str) -> HttpResponse:
    """
    Helper method for generating error repsonses to the website.
    @param request: Pass in the `request` used as a template reference.
    @param pizza: The pizza relevant to the request.
    @param destination: Link to send response to.
    @param error_message: Message communicating what went wrong when processing the request.
    @return An HttpResponse with the `error_message`.
    """
    return render(
        request,
        destination,
        {
            "pizza": pizza,
            "error_message": error_message,
        },
    )

def createPizzaErrorReply(request, toppings_list, destination : str, error_message : str) -> HttpResponse:
    """
    Helper method for generating error repsonses for creating pizzas.
    @param request: Pass in the `request` used as a template reference.
    @param toppings_list: The toppings available for pizza creation.
    @param destination: Link to send response to.
    @param error_message: Message communicating what went wrong when processing the request.
    @return An HttpResponse with the `error_message`.
    """
    return render(
        request,
        destination,
        {
            "toppings_list": toppings_list,
            "error_message": error_message,
        },
    )