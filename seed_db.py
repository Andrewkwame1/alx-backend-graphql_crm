import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order
from django.db import transaction

@transaction.atomic
def seed_database():
    # Clear existing data
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()
    
    # Create customers
    customers = [
        Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
        Customer(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
        Customer(name="Carol Davis", email="carol@example.com", phone="+447700900123"),
        Customer(name="David Wilson", email="david@example.com"),
    ]
    Customer.objects.bulk_create(customers)
    
    # Create products
    products = [
        Product(name="Laptop", price=999.99, stock=10),
        Product(name="Mouse", price=29.99, stock=50),
        Product(name="Keyboard", price=79.99, stock=25),
        Product(name="Monitor", price=299.99, stock=5),
        Product(name="Headphones", price=149.99, stock=15),
    ]
    Product.objects.bulk_create(products)
    
    # Create orders
    customer1 = Customer.objects.get(email="alice@example.com")
    customer2 = Customer.objects.get(email="bob@example.com")
    
    product1 = Product.objects.get(name="Laptop")
    product2 = Product.objects.get(name="Mouse")
    product3 = Product.objects.get(name="Keyboard")
    