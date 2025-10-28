import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    """Filter class for Customer model with name, email, date, and phone filters."""
    
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Name (case-insensitive)"
    )
    email = django_filters.CharFilter(
        field_name="email",
        lookup_expr="icontains",
        label="Email (case-insensitive)"
    )
    created_at_gte = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="gte",
        label="Created at (from date)"
    )
    created_at_lte = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="lte",
        label="Created at (to date)"
    )
    phone_pattern = django_filters.CharFilter(
        method="filter_phone_pattern",
        label="Phone pattern (e.g., starts with +1)"
    )

    def filter_phone_pattern(self, queryset, name, value):
        """Custom filter for phone number pattern matching."""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset

    class Meta:
        model = Customer
        fields = ["name", "email"]


class ProductFilter(django_filters.FilterSet):
    """Filter class for Product model with name, price, and stock filters."""
    
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Name (case-insensitive)"
    )
    price_gte = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Minimum price"
    )
    price_lte = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Maximum price"
    )
    stock_gte = django_filters.NumberFilter(
        field_name="stock",
        lookup_expr="gte",
        label="Minimum stock"
    )
    stock_lte = django_filters.NumberFilter(
        field_name="stock",
        lookup_expr="lte",
        label="Maximum stock"
    )
    low_stock = django_filters.BooleanFilter(
        method="filter_low_stock",
        label="Low stock (< 10)"
    )

    def filter_low_stock(self, queryset, name, value):
        """Custom filter for low stock products."""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = ["name", "price", "stock"]


class OrderFilter(django_filters.FilterSet):
    """Filter class for Order model with amount, date, and related field filters."""
    
    total_amount_gte = django_filters.NumberFilter(
        field_name="total_amount",
        lookup_expr="gte",
        label="Minimum total amount"
    )
    total_amount_lte = django_filters.NumberFilter(
        field_name="total_amount",
        lookup_expr="lte",
        label="Maximum total amount"
    )
    order_date_gte = django_filters.DateFilter(
        field_name="order_date",
        lookup_expr="gte",
        label="Order date (from)"
    )
    order_date_lte = django_filters.DateFilter(
        field_name="order_date",
        lookup_expr="lte",
        label="Order date (to)"
    )
    customer_name = django_filters.CharFilter(
        field_name="customer__name",
        lookup_expr="icontains",
        label="Customer name (case-insensitive)"
    )
    product_name = django_filters.CharFilter(
        field_name="products__name",
        lookup_expr="icontains",
        label="Product name (case-insensitive)"
    )
    product_id = django_filters.NumberFilter(
        field_name="products__id",
        label="Product ID"
    )

    class Meta:
        model = Order
        fields = ["total_amount", "order_date"]