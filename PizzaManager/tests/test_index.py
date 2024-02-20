from django.test import TestCase, Client
from django.test.utils import setup_test_environment, teardown_test_environment
from django.urls import reverse

# Create your tests here.
class TestIndex(TestCase):
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

    def test_home_page(self):
        response = self.client.get(reverse("PizzaManager:index"))
        self.assertEqual(response.status_code, 200)