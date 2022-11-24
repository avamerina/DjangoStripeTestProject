from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name}: ${self.price}"


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='items')
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0.02, validators=[MinValueValidator(0.01), MaxValueValidator(100)])
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.02, validators=[MinValueValidator(0.01), MaxValueValidator(100)])

    def __str__(self):
        return f'{self.id}'
