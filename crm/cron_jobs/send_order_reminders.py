#!/usr/bin/env python
"""
Order Reminders Script
Queries GraphQL endpoint for pending orders (within last 7 days)
and logs reminders to /tmp/order_reminders_log.txt
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
django.setup()

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import requests
import json


def send_order_reminders():
    """Query GraphQL endpoint for recent orders and log reminders"""
    
    try:
        # GraphQL query to get orders from the last 7 days
        query_string = """
        query {
            allOrders(filter: { orderDateGte: "%s" }) {
                edges {
                    node {
                        id
                        customer {
                            name
                            email
                        }
                        totalAmount
                        orderDate
                    }
                }
            }
        }
        """
        
        # Calculate date 7 days ago
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        query_str = query_string % seven_days_ago
        
        # Execute GraphQL query via HTTP
        url = "http://localhost:8000/graphql"
        payload = {"query": query_str}
        
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        # Log timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        
        # Process results and log
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(f"\n{timestamp} - Order Reminders Processed:\n")
            
            if 'data' in data and 'allOrders' in data['data']:
                orders = data['data']['allOrders']['edges']
                
                if not orders:
                    f.write("  No pending orders found.\n")
                    print("Order reminders processed! (No pending orders)")
                else:
                    for order_edge in orders:
                        order = order_edge['node']
                        order_id = order['id']
                        customer_email = order['customer']['email']
                        customer_name = order['customer']['name']
                        total_amount = order['totalAmount']
                        order_date = order['orderDate']
                        
                        reminder = f"  Order #{order_id}: {customer_name} ({customer_email}) - Amount: ${total_amount} - Date: {order_date}\n"
                        f.write(reminder)
                    
                    print(f"Order reminders processed! ({len(orders)} orders found)")
            else:
                f.write("  Error: Could not retrieve orders from GraphQL\n")
                if 'errors' in data:
                    f.write(f"  GraphQL Errors: {data['errors']}\n")
                print("Order reminders processed! (Error retrieving data)")
                
    except requests.exceptions.RequestException as e:
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(f"\n{timestamp} - Error connecting to GraphQL endpoint: {str(e)}\n")
        print(f"Order reminders processed! (Connection error: {str(e)})")
    except Exception as e:
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        with open('/tmp/order_reminders_log.txt', 'a') as f:
            f.write(f"\n{timestamp} - Unexpected error: {str(e)}\n")
        print(f"Order reminders processed! (Error: {str(e)})")


if __name__ == '__main__':
    send_order_reminders()
