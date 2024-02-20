from django.test import TestCase, Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.urls import reverse

from PizzaManager.models import Topping, Pizza

HTTP_OK = 200
HTTP_REDIRECT = 302

# Create your tests here.
class TestPizzas(TestCase):
    """
    Tests that confirm each of the requirements for Pizza functionality are satisfied.
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
    ### It should allow me to see a list of existing pizzas and their toppings ###
    ##############################################################################

    def test_list_available_pizzas_empty(self):
        response = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(response.status_code, HTTP_OK)
        self.assertQuerySetEqual(response.context["pizzas_list"], [])

    def test_list_available_pizzas_contents(self):
        topping1 = Topping.objects.create(name="Test Topping")
        topping2 = Topping.objects.create(name="TestTopping2")
        self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "toppings_options": [topping1, topping2],
            "pizza_new": "pizza_new"
        })
        pizza = Pizza.objects.get(name="TestPizza")
        response = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(response.status_code, HTTP_OK)
        # Verify that the pizza sent corresponds with all the one created in the database.
        self.assertQuerySetEqual(response.context["pizzas_list"], [pizza])
        # Verify that the pizza sent has the same toppings as the one in the database.
        self.assertEqual(response.context["pizzas_list"][0].toppings, pizza.toppings)

    ##############################################################################
    ###    It should allow me to create a new pizza and add toppings to it     ###
    ##############################################################################

    def test_add_pizza_no_toppings(self):
        getPageResponse = self.client.get("/pizza/new")
        self.assertEqual(getPageResponse.status_code, HTTP_OK)
        pizzaPostResponse = self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new"
        })
        self.assertEqual(pizzaPostResponse.status_code, HTTP_REDIRECT)
        self.assertRedirects(pizzaPostResponse, reverse("PizzaManager:Pizza Overview"))

    def test_add_pizza_with_toppings(self):
        topping1 = Topping.objects.create(name="Test Topping")
        topping2 = Topping.objects.create(name="TestTopping2")
        pizzaPostResponse = self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new",
            "toppings_options": [topping1, topping2]
        })

        created_pizza = Pizza.objects.get(name="TestPizza")

        self.assertEqual(pizzaPostResponse.status_code, HTTP_REDIRECT)
        self.assertRedirects(pizzaPostResponse, reverse("PizzaManager:Pizza Overview"))

        createPizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(createPizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(createPizzaResponse.context["pizzas_list"], [created_pizza])
        self.assertContains(createPizzaResponse, topping1)
        self.assertContains(createPizzaResponse, topping2)

    ##############################################################################
    ###             It should allow me to delete an existing pizza             ###
    ##############################################################################

    def test_delete_pizza(self):
        #Ensure adding a pizza is successful.
        self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new"
        })
        pizza = Pizza.objects.get(name="TestPizza")
        addPizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(addPizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addPizzaResponse.context["pizzas_list"], [pizza])

        #Now delete the pizza.
        verifyDeleteResponse = self.client.post(reverse("PizzaManager:Pizza Editor", args=[1,]), {"pizza_delete": "pizza_delete"})
        self.assertEqual(verifyDeleteResponse.status_code, HTTP_REDIRECT)
        deletePizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(deletePizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(deletePizzaResponse.context["pizzas_list"], [])

    ##############################################################################
    ###             It should allow me to update an existing pizza             ###
    ##############################################################################

    def test_update_rename_pizza(self):
        #Ensure adding a pizza is successful.
        self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new"
        })
        pizza = Pizza.objects.get(name="TestPizza")
        addPizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(addPizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addPizzaResponse.context["pizzas_list"], [pizza])

        #Now update/rename the topping.
        verifyUpdateResponse = self.client.post(reverse("PizzaManager:Pizza Editor", args=[1,]), {
            "pizza_name_change": "pizza_name_change",
            "new_name": "PizzaTest"
        })
        self.assertEqual(verifyUpdateResponse.status_code, HTTP_REDIRECT)
        pizza = Pizza.objects.get(name="PizzaTest")
        updatePizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(updatePizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(updatePizzaResponse.context["pizzas_list"], [pizza])

    ##############################################################################
    ###       It should allow me to update toppings on an existing pizza       ###
    ##############################################################################

    def test_update_add_topping_pizza(self):
        #Ensure adding a pizza is successful.
        self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new"
        })
        pizza = Pizza.objects.get(name="TestPizza")
        addPizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(addPizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(addPizzaResponse.context["pizzas_list"], [pizza])
        topping = Topping.objects.create(name="TestTopping")

        #Now add a topping to the pre-existing pizza.
        verifyUpdateResponse = self.client.post(reverse("PizzaManager:Pizza Editor", args=[1,]), {
            "pizza_topping_add": "pizza_topping_add",
            "toppings_options": topping
        })
        self.assertEqual(verifyUpdateResponse.status_code, HTTP_REDIRECT)
        pizza = Pizza.objects.get(name="TestPizza")
        updatePizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))
        self.assertEqual(updatePizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(updatePizzaResponse.context["pizzas_list"], [pizza])
        self.assertContains(updatePizzaResponse, topping)

    def test_update_remove_topping_pizza(self):
        #Create pizza
        topping1 = Topping.objects.create(name="Test Topping")
        topping2 = Topping.objects.create(name="TestTopping2")
        self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "toppings_options": [topping1, topping2],
            "pizza_new": "pizza_new"
        })
        pizza = Pizza.objects.get(name="TestPizza")

        #Call to remove a topping
        verifyUpdateResponse = self.client.post(reverse("PizzaManager:Pizza Editor", args=[1,]), {
            "pizza_topping_delete": "pizza_topping_delete",
            "deleted_topping": topping1
        })

        self.assertEqual(verifyUpdateResponse.status_code, HTTP_REDIRECT)
        updatePizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))

        self.assertEqual(updatePizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(updatePizzaResponse.context["pizzas_list"], [pizza])
        self.assertNotContains(updatePizzaResponse, topping1)
        self.assertContains(updatePizzaResponse, topping2)

    def test_update_change_topping_pizza(self):
        #Create pizza
        topping1 = Topping.objects.create(name="Test Topping")
        topping2 = Topping.objects.create(name="TestTopping2")
        self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "toppings_options": [topping1],
            "pizza_new": "pizza_new"
        })
        pizza = Pizza.objects.get(name="TestPizza")

        #Call to change a topping
        verifyUpdateResponse = self.client.post(reverse("PizzaManager:Pizza Editor", args=[1,]), {
            "pizza_topping_change": "pizza_topping_change",
            "prior_topping" : topping1,
            "toppings_options": [topping2]
        })

        self.assertEqual(verifyUpdateResponse.status_code, HTTP_REDIRECT)
        updatePizzaResponse = self.client.get(reverse("PizzaManager:Pizza Overview"))

        self.assertEqual(updatePizzaResponse.status_code, HTTP_OK)
        self.assertQuerySetEqual(updatePizzaResponse.context["pizzas_list"], [pizza])
        self.assertNotContains(updatePizzaResponse, topping1)
        self.assertContains(updatePizzaResponse, topping2)

    ##############################################################################
    ###           It should not allow me to enter duplicate pizzas             ###
    ##############################################################################

    def test_no_created_duplicate_pizzas(self):
        #Create first pizza
        successPizzaResponse = self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new"
        })
        self.assertEqual(successPizzaResponse.status_code, HTTP_REDIRECT)

        #Create pizza with same name.
        failPizzaResponse= self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new"
        })
        self.assertEqual(failPizzaResponse.status_code, HTTP_OK)
        self.assertEqual(failPizzaResponse.context["error_message"], 
                         "A pizza with this name already exists. Please enter a unique name. No pizza created.")

    def test_no_updated_duplicate_pizzas(self):
        #Create first pizza
        successPizzaResponse = self.client.post("/pizza/new", { 
            "new_pizza_name": "TestPizza",
            "pizza_new": "pizza_new"
        })
        self.assertEqual(successPizzaResponse.status_code, HTTP_REDIRECT)

        #Create second pizza.
        failPizzaResponse = self.client.post("/pizza/new", { 
            "new_pizza_name": "Test Pizza",
            "pizza_new": "pizza_new"
        })
        self.assertEqual(failPizzaResponse.status_code, HTTP_REDIRECT)

        #Rename second pizza to follow the first pizza.
        failPizzaRenameResponse = self.client.post(reverse("PizzaManager:Pizza Editor", args=[2,]), { 
            "new_name": "TestPizza",
            "pizza_name_change": "pizza_name_change"
        })
        self.assertEqual(failPizzaRenameResponse.status_code, HTTP_OK)
        self.assertEqual(failPizzaRenameResponse.context["error_message"], 
                         "A pizza with this name already exists. Please enter a unique name. Name unchanged.")
