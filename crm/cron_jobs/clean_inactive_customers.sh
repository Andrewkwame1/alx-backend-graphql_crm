#!/bin/bash

# Customer Cleanup Script
# Deletes customers with no orders since a year ago
# Logs results to /tmp/customer_cleanup_log.txt

cd "$(dirname "$0")/../../" || exit

# Execute Django shell command to delete inactive customers
python manage.py shell << EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer
from django.db.models import Q

# Find customers with no orders in the last year
one_year_ago = timezone.now() - timedelta(days=365)

# Get customers who have no orders or whose last order is older than a year
inactive_customers = Customer.objects.filter(
    Q(orders__isnull=True) | Q(orders__order_date__lt=one_year_ago)
).distinct()

deleted_count = len(inactive_customers)

# Delete inactive customers
for customer in inactive_customers:
    customer.delete()

# Log the results
import datetime
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open('/tmp/customer_cleanup_log.txt', 'a') as f:
    f.write(f"{timestamp} - Deleted {deleted_count} inactive customers\n")

print(f"Deleted {deleted_count} inactive customers")
EOF
