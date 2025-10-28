# CRM Weekly Report Setup Guide

This guide provides step-by-step instructions to set up Celery and Celery Beat for automated weekly CRM report generation.

## Overview

The system generates a weekly CRM report (scheduled for Monday at 6:00 AM) that summarizes:
- Total number of customers
- Total number of orders
- Total revenue from all orders

The report is logged to `/tmp/crm_report_log.txt` with timestamps.

## Prerequisites

- Django 4.0+
- Python 3.8+
- Redis server running

## Installation Steps

### 1. Install Dependencies

All required packages are already in `requirements.txt`:
- `celery==5.3.6`
- `redis==5.0.1`
- `django-celery-beat`

If not already installed, run:
```bash
pip install -r requirements.txt
```

### 2. Install Redis

**On Linux/Mac:**
```bash
# Using Homebrew (macOS)
brew install redis
brew services start redis

# Using apt (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**On Windows:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use Windows Subsystem for Linux (WSL) and install Redis there
- Or use Docker: `docker run -d -p 6379:6379 redis`

### 3. Run Migrations

Initialize the database with django-celery-beat tables:
```bash
python manage.py migrate
```

## Running the System

### Terminal 1: Start Django Development Server

```bash
python manage.py runserver
```

The GraphQL endpoint will be available at `http://127.0.0.1:8000/graphql/`

### Terminal 2: Start Celery Worker

```bash
celery -A crm worker -l info
```

This worker processes Celery tasks. Output will show task processing in real-time.

### Terminal 3: Start Celery Beat

```bash
celery -A crm beat -l info
```

Celery Beat handles scheduling and dispatches the `generate_crm_report` task every Monday at 6:00 AM.

## Verification

### Check Log File

Monitor the weekly report logs:
```bash
tail -f /tmp/crm_report_log.txt
```

**Expected log format:**
```
2025-10-28 06:00:00 - Report: 10 customers, 25 orders, 1500.50 revenue
2025-11-04 06:00:00 - Report: 12 customers, 28 orders, 1750.75 revenue
```

### Manual Task Execution (Testing)

To test the task without waiting for Monday 6 AM:

```bash
# In Django shell
python manage.py shell
```

Then run:
```python
from crm.tasks import generate_crm_report
generate_crm_report.apply_async()
# Or synchronously:
generate_crm_report()
```

### GraphQL Query (Manual Report Generation)

Query the CRM data manually via GraphQL:

```graphql
query {
  totalCustomerCount
  totalOrderCount
  totalRevenue
}
```

Using curl:
```bash
curl -X POST http://127.0.0.1:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ totalCustomerCount totalOrderCount totalRevenue }"}'
```

## Configuration Details

### Celery Settings (crm/settings.py)

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),  # Mondays at 6 AM
    },
}
```

### Task Definition (crm/tasks.py)

The `generate_crm_report` task:
1. Queries the GraphQL endpoint for total customers, orders, and revenue
2. Formats the data with a timestamp
3. Appends the report to `/tmp/crm_report_log.txt`
4. Logs any errors that occur during execution

### GraphQL Schema Extensions (crm/schema.py)

New query fields for report generation:
- `totalCustomerCount`: Returns total number of customers
- `totalOrderCount`: Returns total number of orders
- `totalRevenue`: Returns sum of all order amounts (as Decimal)

## Troubleshooting

### Redis Connection Error
```
ERROR: Cannot connect to Redis at localhost:6379
```
**Solution:** Ensure Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Task Not Being Scheduled
1. Check Celery Beat logs for scheduling errors
2. Verify `CELERY_BEAT_SCHEDULE` in `crm/settings.py`
3. Run migrations to create django-celery-beat tables
4. Restart Celery Beat

### Log File Not Updating
1. Verify `/tmp/` directory is writable: `touch /tmp/test.txt`
2. Check Celery worker logs for task execution errors
3. Test the task manually in Django shell (see Verification section)

### GraphQL Query Returns Null
1. Ensure Django dev server is running
2. Check that database has sample data (run seed_db.py if needed)
3. Verify GraphQL endpoint: `curl http://127.0.0.1:8000/graphql/`

## Production Deployment

For production:
1. Use a message broker like RabbitMQ or Redis with password authentication
2. Run Celery worker(s) as system services (systemd/supervisord)
3. Use a process manager like Supervisor for Celery Beat
4. Store logs in a persistent location (not `/tmp`)
5. Configure log rotation for the report log file

## File Reference

- `crm/celery.py` - Celery app initialization
- `crm/__init__.py` - Celery app loader
- `crm/tasks.py` - Task definitions
- `crm/settings.py` - Celery configuration
- `crm/schema.py` - GraphQL schema with report query fields
- `requirements.txt` - Python dependencies
