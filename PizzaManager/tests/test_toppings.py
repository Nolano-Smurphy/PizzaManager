from django.test import TestCase, Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.urls import reverse

from PizzaManager.models import Topping

HTTP_OK = 200
HTTP_REDIRECT = 302

# Create your tests here.
class TestToppings(TestCase):
    """
    Tests that confirm each of the requirements for Topping functionality are satisfied.
    """

    @classmethod
    def setUpClass(self):
        teardown_test_environment()
        setup_test_environment()
        return super().setUpClass()

    def setUp(self):
        self.client = Client()
        return super().setUp()

    ##############################################################################
    ###         It should allow me to see a list of available toppings         ###
    ##############################################################################

    def test_list_available_toppings_empty(self):
        """
        This test will ensure the client receives an empty list if nothing is in the database when
        the overview menu is requested.
        """
        response = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertQuerySetEqual(response.context["toppings_list"], [])

    def test_list_available_toppings_contents(self):
        """
        This test will ensure the client receives a filled list if something is in the database when
        the overview menu is requested.
        """
        self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        topping = Topping.objects.get(name="TestTopping")
        response = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertQuerySetEqual(response.context["toppings_list"], [topping])

    ##############################################################################
    ###                It should allow me to add a new topping                 ###
    ##############################################################################

    def test_add_topping(self):
        """
        This test will ensure the server correctly redirects the client and returns a
        filled toppings list when going back to the Topping Overview after requesting a topping addition.
        """
        getPageResponse = self.client.get("/toppings/new")
        self.assertEqual(getPageResponse.status_code, HTTP_OK)
        toppingPostResponse = self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        topping = Topping.objects.get(name="TestTopping")

        self.assertEqual(toppingPostResponse.status_code, HTTP_REDIRECT)
        self.assertRedirects(toppingPostResponse, reverse("PizzaManager:Toppings Overview"))
        addToppingResponse = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(addToppingResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addToppingResponse.context["toppings_list"], [topping])

    ##############################################################################
    ###            It should allow me to delete an existing topping            ###
    ##############################################################################

    def test_delete_topping(self):
        """
        This test will ensure the server correctly redirects the client and returns a
        filled toppings list when going back to the Topping Overview after requesting a topping deletion.
        """
        #Ensure adding a topping is successful.
        self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        topping = Topping.objects.get(name="TestTopping")
        addToppingResponse = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(addToppingResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addToppingResponse.context["toppings_list"], [topping])

        #Now delete the topping.
        verifyDeleteResponse = self.client.post(reverse("PizzaManager:Toppings Editor", args=[1,]), {"topping_delete": "topping_delete"})
        self.assertEqual(verifyDeleteResponse.status_code, HTTP_REDIRECT)
        deleteToppingResponse = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(deleteToppingResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(deleteToppingResponse.context["toppings_list"], [])

    
    ##############################################################################
    ###           It should allow me to update an existing topping             ###
    ##############################################################################

    def test_update_topping(self):
        """
        This test will ensure the server correctly redirects the client and returns a
        filled toppings list when going back to the Topping Overview after requesting a topping rename.
        """
        #Ensure adding a topping is successful.
        self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        topping = Topping.objects.get(name="TestTopping")
        addToppingResponse = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(addToppingResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addToppingResponse.context["toppings_list"], [topping])

        #Now update/rename the topping.
        verifyUpdateResponse = self.client.post(reverse("PizzaManager:Toppings Editor", args=[1,]), {
            "topping_name_change": "topping_name_change",
            "new_name": "ToppingTest"
        })
        self.assertEqual(verifyUpdateResponse.status_code, HTTP_REDIRECT)
        topping = Topping.objects.get(name="ToppingTest")
        updateToppingResponse = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(updateToppingResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(updateToppingResponse.context["toppings_list"], [topping])

    ##############################################################################
    ###          It should not allow me to enter duplicate toppings            ###
    ##############################################################################

    def test_no_created_duplicate_toppings(self):
        """
        This test will ensure the server keeps the client on the Topping Create page and returns an
        error message when they enter a name for a new topping when a topping with that name already exists.
        """
        #Ensure adding first topping is successful.
        firstToppingResponse = self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        self.assertEqual(firstToppingResponse.status_code, HTTP_REDIRECT)
        topping = Topping.objects.get(name="TestTopping")
        addToppingResponse = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(addToppingResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addToppingResponse.context["toppings_list"], [topping])

        #Try adding duplicate topping and verify fail.
        secondToppingResponse = self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        self.assertEqual(secondToppingResponse.status_code, HTTP_OK)
        self.assertEqual(secondToppingResponse.context["error_message"], 
                         "A topping with this name already exists. Please enter a unique name. No topping created.")
        
    def test_no_updated_duplicate_toppings(self):
        """
        This test will ensure the server keeps the client on the Topping Editor page and returns an
        error message when they enter a name for an existing topping when a topping with that name already exists.
        """

        #Ensure adding first topping is successful.
        firstToppingResponse = self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        self.assertEqual(firstToppingResponse.status_code, HTTP_REDIRECT)

        secondToppingResponse = self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping2",
            "topping_new": "topping_new"
        })
        self.assertEqual(secondToppingResponse.status_code, HTTP_REDIRECT)

        topping = Topping.objects.get(name="TestTopping")
        topping2 = Topping.objects.get(name="TestTopping2")
        addToppingResponse = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(addToppingResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addToppingResponse.context["toppings_list"], [topping, topping2])

        #Try adding duplicate topping and verify fail.
        duplicateToppingResponse = self.client.post(reverse("PizzaManager:Toppings Editor", args=[1,]), {
            "topping_name_change": "topping_name_change",
            "new_name": "TestTopping"
        })
        self.assertEqual(duplicateToppingResponse.status_code, HTTP_OK)
        self.assertEqual(duplicateToppingResponse.context["error_message"], 
                         "A topping with this name already exists. Please enter a unique name. Name unchanged.")