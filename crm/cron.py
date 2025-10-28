import logging
from datetime import datetime
import requests
import json
from datetime import datetime
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

def log_crm_heartbeat():
    """Logs a heartbeat message every 5 minutes and optionally checks GraphQL API."""
    log_file = "/tmp/crm_heartbeat_log.txt"

    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Write to log file (append mode)
    with open(log_file, "a") as f:
        f.write(message + "\n")

    # Optional: verify GraphQL hello field
    try:
        query = {"query": "{ hello }"}
        response = requests.post("http://localhost:8000/graphql", json=query, timeout=5)
        if response.status_code == 200:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello response: {response.json()}\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint error: {response.status_code}\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {e}\n")



def update_low_stock():
    url = "http://127.0.0.1:8000/graphql/"
    query = """
    mutation {
        updateLowStockProducts {
            success
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """

    try:
        response = requests.post(url, json={'query': query})
        result = response.json()

        log_file = "/tmp/low_stock_updates_log.txt"
        with open(log_file, "a") as f:
            f.write(f"\n--- {datetime.now()} ---\n")
            if "errors" in result:
                f.write("Errors: " + str(result["errors"]) + "\n")
            else:
                data = result["data"]["updateLowStockProducts"]
                f.write(data["message"] + "\n")
                for p in data["updatedProducts"]:
                    f.write(f"{p['name']} updated stock: {p['stock']}\n")
    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"\n--- {datetime.now()} ---\nError: {str(e)}\n")