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
- Redis server running (or Docker)
- Virtual environment (venv or conda)

## Installation Steps

### 1. Set Up Virtual Environment

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you encounter a PowerShell execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

All required packages are in `requirements.txt`:
- `celery==5.3.6`
- `redis==5.0.1`
- `django-celery-beat`
- `django-crontab`
- `graphene-django`
- `django-filter`

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Install Redis

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

Option A: Windows Subsystem for Linux (WSL) - Recommended
```bash
# Enable WSL and install Ubuntu
wsl --install

# Inside WSL Ubuntu:
sudo apt-get update
sudo apt-get install redis-server
sudo service redis-server start
```

Option B: Docker
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

Option C: Manual Download
- Download from: https://github.com/microsoftarchive/redis/releases
- Extract and add to PATH, or run directly

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 4. Run Migrations

Initialize the database with django-celery-beat tables:
```bash
python manage.py migrate
```

### 5. Load Sample Data (Optional)

To populate the database with test data:
```bash
python seed_db.py
```

## Running the System

### Environment Setup

Before starting services, set the Django settings module (required for Celery):

**On Linux/Mac/WSL:**
```bash
export DJANGO_SETTINGS_MODULE=alx_backend_graphql_crm.settings
```

**On Windows (PowerShell):**
```powershell
$env:DJANGO_SETTINGS_MODULE='alx_backend_graphql_crm.settings'
```

### Terminal 1: Start Django Development Server

```bash
python manage.py runserver
```

The GraphQL endpoint will be available at `http://127.0.0.1:8000/graphql/`

### Terminal 2: Start Celery Worker

**On Linux/Mac/WSL:**
```bash
celery -A crm worker -l info
```

**On Windows (PowerShell):**
```powershell
celery -A crm worker -l info --pool=solo
```

(Note: Windows requires the `--pool=solo` flag to avoid multiprocessing issues)

This worker processes Celery tasks. Output will show task processing in real-time.

### Terminal 3: Start Celery Beat

**On Linux/Mac/WSL:**
```bash
celery -A crm beat -l info
```

**On Windows (PowerShell):**
```powershell
celery -A crm beat -l info
```

Celery Beat handles scheduling and dispatches the `generate_crm_report` task every Monday at 6:00 AM.

## Verification

### Check Redis Connection

Verify Redis is running and accessible:
```bash
redis-cli ping
# Should return: PONG

# Check Redis info:
redis-cli info server
```

### Check Log File

Monitor the weekly report logs:

**On Linux/Mac/WSL:**
```bash
tail -f /tmp/crm_report_log.txt
```

**On Windows (PowerShell):**
```powershell
# View log file
Get-Content "C:\Temp\crm_report_log.txt" -Tail 20 -Wait
```

**Expected log format:**
```
2025-10-28 06:00:00 - Report: 10 customers, 25 orders, 1500.50 revenue
2025-11-04 06:00:00 - Report: 12 customers, 28 orders, 1750.75 revenue
```

### Check Celery Beat Schedule

Verify the scheduled task is registered:
```bash
# In another terminal, check if Beat is scheduling tasks correctly
# Look for output like: "Scheduler: Sending due task generate-crm-report"
```

### Manual Task Execution (Testing)

To test the task without waiting for Monday 6 AM:

**In Django shell:**
```bash
python manage.py shell
```

Then run:
```python
from crm.tasks import generate_crm_report

# Execute task asynchronously (via Celery)
result = generate_crm_report.apply_async()
print(f"Task ID: {result.id}")

# Or execute synchronously (for testing)
generate_crm_report()
```

Then check the log file to verify the report was generated.

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

**Expected response:**
```json
{
  "data": {
    "totalCustomerCount": 10,
    "totalOrderCount": 25,
    "totalRevenue": 1500.5
  }
}
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
**Solutions:**
1. Ensure Redis is running: `redis-cli ping` (should return `PONG`)
2. Check Redis port: `redis-cli -p 6379 ping`
3. On Windows, verify Docker container is running: `docker ps | grep redis`
4. If using WSL, ensure service is started: `sudo service redis-server start`

### Celery Worker Not Processing Tasks
1. **Check worker is running:** Look for "Celery worker online" in terminal 2
2. **Verify DJANGO_SETTINGS_MODULE is set:** Run `echo $DJANGO_SETTINGS_MODULE` (Linux/Mac) or `$env:DJANGO_SETTINGS_MODULE` (Windows PowerShell)
3. **Check for import errors:** Look at worker logs for "ModuleNotFoundError" or similar
4. **Restart worker:** Stop (Ctrl+C) and restart `celery -A crm worker -l info`

### Task Not Being Scheduled
1. **Check Celery Beat is running:** Should see "Scheduler: Sending due task..." messages
2. **Verify `CELERY_BEAT_SCHEDULE` in `crm/settings.py`:** Ensure format is correct
3. **Run migrations:** `python manage.py migrate` (creates ScheduledTask table for Beat)
4. **Check system time:** Ensure server time is correct (Beat uses system clock)
5. **Restart Beat:** Stop (Ctrl+C) and restart `celery -A crm beat -l info`

### Log File Not Updating
1. **Verify log directory is writable:**
   - Linux/Mac: `touch /tmp/crm_report_log.txt`
   - Windows: `New-Item -Path "C:\Temp" -Name "crm_report_log.txt" -ItemType File` (create C:\Temp if needed)
2. **Check Celery worker logs for errors** in terminal 2
3. **Test task manually** in Django shell (see Verification section)
4. **Check GraphQL endpoint is accessible:** `curl http://127.0.0.1:8000/graphql/`

### GraphQL Query Returns Null
1. **Ensure Django dev server is running** (terminal 1)
2. **Check database has sample data:** Run `python seed_db.py`
3. **Verify GraphQL endpoint:** `curl http://127.0.0.1:8000/graphql/`
4. **Test a simple query:**
   ```bash
   curl -X POST http://127.0.0.1:8000/graphql/ \
     -H "Content-Type: application/json" \
     -d '{"query": "{ hello }"}'
   ```

### ModuleNotFoundError in Celery
```
ModuleNotFoundError: No module named 'crm'
```
**Solution:** Ensure you're running Celery from the project root directory with `DJANGO_SETTINGS_MODULE` set:
```bash
export DJANGO_SETTINGS_MODULE=alx_backend_graphql_crm.settings
celery -A crm worker -l info
```

### Windows: "AttributeError: 'NoneType' object has no attribute 'sem_open'"
**Solution:** Use `--pool=solo` flag with Celery worker:
```powershell
celery -A crm worker -l info --pool=solo
```

## Production Deployment

For production environments:

1. **Use a robust message broker:**
   - Redis with password authentication and persistence
   - RabbitMQ (more reliable for large-scale deployments)

2. **Run Celery as system services:**
   - Linux: Use systemd (create `.service` files for worker and beat)
   - Windows: Use NSSM (Non-Sucking Service Manager) or Task Scheduler

3. **Use a process manager:**
   - Supervisor for managing worker/beat processes
   - Systemd for Linux systems

4. **Persistent logging:**
   - Store logs in `/var/log/` (Linux) or `C:\Logs\` (Windows)
   - Configure log rotation with logrotate or similar

5. **Database configuration:**
   - Use a persistent database (PostgreSQL recommended)
   - Set up automated backups

6. **Monitor and alert:**
   - Monitor Celery task processing (use Flower: `pip install flower`)
   - Set up alerts for failed tasks
   - Monitor Redis/broker health

### Example: Running with Flower (Web Dashboard)

Install Flower:
```bash
pip install flower
```

Start Flower (requires Celery worker running):
```bash
celery -A crm events
# In another terminal:
celery -A crm flower --port=5555
```

Access dashboard at `http://localhost:5555`

## File Reference

- `crm/celery.py` - Celery app initialization
- `crm/__init__.py` - Celery app loader
- `crm/tasks.py` - Task definitions
- `crm/settings.py` - Celery configuration
- `crm/schema.py` - GraphQL schema with report query fields
- `requirements.txt` - Python dependencies
