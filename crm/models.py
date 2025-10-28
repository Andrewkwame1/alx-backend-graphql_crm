from datetime import timezone
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$',
                message="Phone must be in the format +1234567890 or 123-456-7890"
            )
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} for {self.customer.name}"
