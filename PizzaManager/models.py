from django.db import models

# Create your models here.
class Toppings(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Pizza(models.Model):
    name = models.CharField(max_length=50)
    toppings = models.ManyToManyField(Toppings)

    def __str__(self):
        return self.name