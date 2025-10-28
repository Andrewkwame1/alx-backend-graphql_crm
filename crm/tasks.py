from celery import shared_task
import requests
from datetime import datetime

@shared_task
def generate_crm_report():
    url = "http://127.0.0.1:8000/graphql/"
    query = """
    query {
        totalCustomerCount
        totalOrderCount
        totalRevenue
    }
    """
    try:
        response = requests.post(url, json={'query': query})
        data = response.json()

        # Extract data
        customers = data['data']['totalCustomerCount']
        orders = data['data']['totalOrderCount']
        revenue = data['data']['totalRevenue']

        log_file = "/tmp/crm_report_log.txt"
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report: "
                    f"{customers} customers, {orders} orders, {revenue} revenue\n")
    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error: {str(e)}\n")