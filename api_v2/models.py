from datetime import datetime

from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=300, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name}: {self.price}"


class Order(models.Model):
    items = models.ManyToManyField(Product, related_name='items')

    def __str__(self):
        return f'{self.id}'


