# Cloud Warehouse Platform — Notification System Audit

This document presents the read-only audit of the notification and email delivery pipeline.

---

## 1. Current Architecture Flow

```
BUSINESS EVENT (e.g., USER_LOGIN, TASK_COMPLETED, ADMIN_CREATION)
 ↓
NOTIFICATION EVENT (publish_event / create_security_event)
 ↓
NOTIFICATION SERVICE (checks preferences, creates DB Notification records)
 ↓
RECIPIENT RESOLUTION (resolve_recipients based on severity, roles, and warehouse assignments)
 ↓
EMAIL QUEUE (Celery task delay if CELERY_ENABLED=true, else thread/BackgroundTasks fallback)
 ↓
EMAIL PROVIDER (SMTP in notifications.py OR Resend API in resend_client.py)
 ↓
RECIPIENT INBOX
```

---

## 2. Notification Service & Email Provider Integration

The system currently has two parallel email sending pathways:
1. **SMTP Pathway** ([`backend/notifications.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/notifications.py)):
   - Used for Admin OTP passkeys and legacy event notifications.
   - Connects to an SMTP server using `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD` environment variables.
2. **Resend API Pathway** ([`backend/resend_client.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/resend_client.py)):
   - Used by Celery tasks (`send_resend_email_task`, `send_generic_email_task`) and security alerts in `security_service.py` (via fallback).
   - Connects directly to the Resend API using the `RESEND_API_KEY` SDK client.

---

## 3. Current Broken Links & Root Causes

### A. SMTP Authentication Failure (Broken Credentials)
* **Description**: The SMTP settings in `.env` are mismatched and invalid:
  ```env
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=onboarding@resend.dev
  SMTP_PASSWORD=suqipgfzssznfqmn
  ```
  Here, `onboarding@resend.dev` (a Resend sandbox address) is being used as the username to log into `smtp.gmail.com` (Google Gmail SMTP host) with a Gmail App Password. This causes SMTP login to fail with `Authentication Failed` (454 / 535 error).
* **Impact**: All OTP emails (e.g., creating a new administrator) and legacy fallback alerts fail to send.

### B. No Running Celery Worker Process
* **Description**: Although `CELERY_ENABLED=true` is set in `.env` and RabbitMQ/Redis are fully online, there is no active `celery worker` process running on the host system.
* **Impact**: All emails dispatched asynchronously via Celery (`send_resend_email_task.delay()`) sit indefinitely in the RabbitMQ broker queue and are never picked up or delivered.

### C. Missing User Email Addresses in Database
* **Description**: The default admin creation in `backend/init_db.py` and test users creation in `tests/conftest.py` set the `email` field of all seeded users (`admin`, `test_admin`, `test_manager`, etc.) to `None`.
* **Impact**: Since `u.email` is empty, recipient resolution in `publish_event` (`if email_ok and u.email:`) evaluates to `False`, meaning standard notifications (task changes, robot assignments, route failures, AI recommendations, etc.) are never queued or created for email delivery.

### D. Inconsistent Email Clients
* **Description**: Admin creation verification OTPs and normal event notifications go through `notifications.py` (SMTP). Security alerts and Celery email tasks go through `resend_client.resend` (Resend API).
* **Impact**: This creates fragmented behaviors where some actions attempt broken SMTP delivery while others attempt queueing in a worker queue that is not running.

---

## 4. Minimal Fix Plan

1. **Reroute SMTP to Resend API**:
   - Update `send_email_alert` in [`backend/notifications.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/notifications.py) to check if `RESEND_API_KEY` is present.
   - If present, import and delegate email dispatch directly to `resend_client.send_html_email`, bypassing the broken SMTP login cycle while retaining the original SMTP code as a fallback.
2. **Assign Seeded User Emails**:
   - Update `backend/init_db.py` and `tests/conftest.py` (and optionally execute a one-time SQL query) to assign a valid email (e.g. `harsha200797@gmail.com`) to the seeded `admin` and `test_admin` user accounts so recipient resolution finds a valid destination address.
3. **Launch Background Celery Worker**:
   - Start a local background Celery worker process (`celery -A backend.celery_app worker --loglevel=info -P solo`) in the dev environment to process queued emails.
4. **Consolidate HTML Body Wrapper**:
   - Update `send_html_email` in [`backend/resend_client.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/resend_client.py) to check if the body is already HTML (e.g., starts with `<` or contains `<html>`) to avoid double-wrapping email bodies.
