from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import logging

from .models import Topping, Pizza

# Create your views here.
def index(request):
    """
    This view serves as the homepage for the site and asks if the user is either an Owner or a Chef.
    """
    return HttpResponse(render(request, "PizzaManager/landing_page.html"))

def toppings_overview(request):
    """
    This is the view responsible for providing a list of all available toppings to the Owner.
    """
    toppings_list = Topping.objects.order_by("name")[:10]
    context = {"toppings_list": toppings_list}
    return HttpResponse(render(request, "PizzaManager/toppings_overview.html", context))

def toppings_editor(request, topping_id):
    """
    This is the view responsible for handling all changes that might need to occur to a topping.
    """
    topping = get_object_or_404(Topping, pk=topping_id)
    return render(request, "PizzaManager/toppings_editor.html", {"topping": topping})

def pizza_overview(request):
    """
    This is the view responsible for providing a list of all available pizzas to the Chef.
    """
    pizzas_list = Pizza.objects.order_by("name")[:5]
    context = {"pizzas_list": pizzas_list}
    return HttpResponse(render(request, "PizzaManager/pizza_overview.html", context))

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
            if request.POST["new_name"] != "":
                if not hasSpecialChar(request.POST["new_name"]):
                    pizza.name = request.POST["new_name"]
                    pizza.save()
                else:
                    return createPizzaErrorReply(
                        request, 
                        pizza, 
                        destination="PizzaManager/pizza_editor.html",
                        error_message="Please do not include any special characters in the pizza name."
                    )
            else:
                return createPizzaErrorReply(
                    request, 
                    pizza, 
                    destination="PizzaManager/pizza_editor.html",
                    error_message="Received blank. Name unchanged."
                )

        # Process pizza deletions
        elif "pizza_delete" in request.POST:
            return createPizzaErrorReply(
                request, 
                pizza, 
                destination="PizzaManager/pizza_editor.html",
                error_message="This feature has not been implemented yet."
            )

    # Should never occur on production if I did this right.
    except(KeyError):
        logging.exception(KeyError.__traceback__)
        return render(
                request,
                "PizzaManager/pizza_editor.html",
                {
                    "pizza": pizza,
                    "error_message": "Internal Error occurred. Contact Nolan Murphy about resolving this.",
                },
            )
    
    except (Pizza.DoesNotExist):
        return render(
            request,
            "PizzaManager/pizza_editor.html",
            {
                "pizza": pizza,
                "error_message": "You have attempted to alter a pizza that does not exist.",
            },
        )
    
    except (Topping.DoesNotExist):
        return render(
            request,
            "PizzaManager/pizza_editor.html",
            {
                "pizza": pizza,
                "error_message": "You have attempted to alter a topping that does not exist.",
            },
        )
    # Exceptions hopefully won't occur, but it's better to be prepared.
    else:
        return HttpResponseRedirect(reverse("PizzaManager:Pizza Editor", args=(pizza.id,)))

def hasSpecialChar(data_to_validate : str):
    """
    Helper method to make sure the string passed in contains no special characters.
    """
    
    for char in data_to_validate:
        if not (char.isalnum() or char.isspace()):
            return True

    return False

def createPizzaErrorReply(request, pizza, destination : str, error_message : str):
    """
    Helper method for generating error repsonses to the website.
    @param request: Pass in the `request` this is responding to.
    @param pizza: The pizza relevant to the request.
    @param destination: Link to send response to.
    @param error_message: Message communicating what went wrong when processing the request.
    """
    return render(
        request,
        destination,
        {
            "pizza": pizza,
            "error_message": error_message,
        },
    )