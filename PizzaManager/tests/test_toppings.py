from django.test import TestCase, Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.urls import reverse

from PizzaManager.models import Topping

HTTP_OK = 200
HTTP_REDIRECT = 302
HTTP_NOT_FOUND = 404

# Create your tests here.
class TestToppings(TestCase):
    """
    Tests that the home page loads in properly. This is mostly included to test that the app can run.
    """

    @classmethod
    def setUpClass(self):
        teardown_test_environment()
        setup_test_environment()
        return super().setUpClass()

    def setUp(self):
        self.client = Client()
        return super().setUp()

    def test_list_available_toppings_empty(self):
        response = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertQuerySetEqual(response.context["toppings_list"], [])

    def test_list_available_toppings_contents(self):
        self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        topping = Topping.objects.get(name="TestTopping")
        response = self.client.get(reverse("PizzaManager:Toppings Overview"))
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertQuerySetEqual(response.context["toppings_list"], [topping])

    def test_add_topping(self):
        getPageResponse = self.client.get("/toppings/new")
        self.assertEqual(getPageResponse.status_code, HTTP_OK)
        toppingPostResponse = self.client.post("/toppings/new", { 
            "new_topping_name": "TestTopping",
            "topping_new": "topping_new"
        })
        self.assertEqual(toppingPostResponse.status_code, HTTP_REDIRECT)
        self.assertRedirects(toppingPostResponse, reverse("PizzaManager:Toppings Overview"))

    def test_delete_topping(self):
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

    def test_update_topping(self):
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

    def test_no_created_duplicate_toppings(self):
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