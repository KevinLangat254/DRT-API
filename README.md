## Receipt Tracker API

Backend API built with Django and Django REST Framework to record, categorize, and retrieve receipts with user authentication and per-user data isolation.

### Tech Stack
- Django 5
- Django REST Framework
- django-filter
- MySQL (configurable)

### Project Structure (relevant)
- `receipt_tracker/receipt_tracker/` – project settings and URLs
- `receipt_tracker/DRT/` – app (models, serializers, views, urls)
  - `api_urls.py` – all API routes under `/api/`
  - `urls.py` – web routes under `/drt/` (login, logout, register, home)

---

## Setup

1) Create and activate a virtual environment (Windows PowerShell):
```
python -m venv venv
venv\Scripts\Activate.ps1
```

2) Install dependencies:
```
pip install Django djangorestframework django-filter mysqlclient
```

3) Configure database (default is MySQL). Update `DATABASES` in `receipt_tracker/receipt_tracker/settings.py` as needed.

4) Apply migrations and run server:
```
cd receipt_tracker
python manage.py migrate
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000/`.

### Running Tests

Unit tests are included for models and APIs. Tests run against an in-memory SQLite database (overridden in tests), so you do not need MySQL running to execute the test suite.

```
cd receipt_tracker
venv\Scripts\python.exe manage.py test
```

Notes:
- Some unauthenticated API responses may return 401 or 403 depending on authentication/CSRF context during testing. Tests account for this.

---

## Authentication

- Default authentication: DRF Token and Session auth
- Obtain token:
```
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "<your_username>", "password": "<your_password>"}'
```
Use the returned token with: `Authorization: Token <token>`

Web auth (optional UI):
- `GET /drt/login/`, `POST /drt/login/`
- `GET /drt/register/`

API auth endpoints:
- `POST /api/auth/register/` → create user and return `{ token, user }`
- `POST /api/auth/token/` → login, return `{ token }`
- `POST /api/auth/logout/` → logout (invalidate token). Note: POST only; a GET will not log out.

Browsable API tip: When viewing `/api/auth/logout/` in the DRF browser, use the POST form while authenticated.

---

## Base URL

All API endpoints are prefixed with `/api/`.

---

## Endpoints

### Users (current user only)
- `GET /api/users/` – list (single item: your profile)
- `GET /api/users/profile/` – your profile
- `PATCH /api/users/update_profile/` – update your profile (e.g., email)
- `POST /api/users/deactivate/` – deactivate your account (soft delete)


### Categories
- `GET /api/categories/`
- `POST /api/categories/`
- `GET /api/categories/{id}/`
- `PUT/PATCH /api/categories/{id}/`
- `DELETE /api/categories/{id}/`

### Payment Methods
- `GET /api/payment-methods/`
- `POST /api/payment-methods/`
- `GET /api/payment-methods/{id}/`
- `PUT/PATCH /api/payment-methods/{id}/`
- `DELETE /api/payment-methods/{id}/`

### Receipts
- `GET /api/receipts/` – list your receipts
- `POST /api/receipts/` – create
- `GET /api/receipts/{id}/` – retrieve
- `PUT/PATCH /api/receipts/{id}/` – update
- `DELETE /api/receipts/{id}/` – delete
- `GET /api/receipts/analytics/?days=30` – summaries (totals, by category, by payment method, by month)

Receipt fields: `user (auto)`, `category (id)`, `store_name`, `total_amount`, `currency`, `purchase_date`, `notes`

Validations:
- Amounts > 0
- Dates cannot be in the future

Filters (query params on `GET /api/receipts/`):
- `category` – category id
- `purchase_date` – exact date (YYYY-MM-DD)
- `date_from`, `date_to` – range
- `amount_min`, `amount_max` – numeric range
- `payment_method` – payment method name contains
- `tags` – comma-separated tag names

Pagination: page/size via DRF PageNumberPagination (default page size 20)

### Tags and Receipt Tags
- `GET/POST /api/tags/`, `GET/PUT/PATCH/DELETE /api/tags/{id}/`
- `GET/POST /api/receipt-tags/`, `GET/PUT/PATCH/DELETE /api/receipt-tags/{id}/`

### Receipt Items
- `GET/POST /api/receipt-items/`, `GET/PUT/PATCH/DELETE /api/receipt-items/{id}/`

### Receipt Payments
- `GET/POST /api/receipt-payments/`, `GET/PUT/PATCH/DELETE /api/receipt-payments/{id}/`

---

## Usage Examples

Assume `TOKEN=<your_token>`.

Create a receipt:
```
curl -X POST http://127.0.0.1:8000/api/receipts/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 1,
    "store_name": "Acme Supermarket",
    "total_amount": "123.45",
    "currency": "USD",
    "purchase_date": "2025-08-01",
    "notes": "Weekly groceries"
  }'
```

List receipts (date range + payment method filter):
```
curl -H "Authorization: Token $TOKEN" \
  "http://127.0.0.1:8000/api/receipts/?date_from=2025-08-01&date_to=2025-08-31&payment_method=Visa"
```

Analytics (last 90 days):
```
curl -H "Authorization: Token $TOKEN" \
  "http://127.0.0.1:8000/api/receipts/analytics/?days=90"
```

Add a receipt item:
```
curl -X POST http://127.0.0.1:8000/api/receipt-items/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": 10,
    "item_name": "Bananas",
    "quantity": 3,
    "unit_price": "0.60",
    "total_price": "1.80"
  }'
```

Tag a receipt:
```
curl -X POST http://127.0.0.1:8000/api/receipt-tags/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": 10,
    "tag": 2
  }'
```

---

## Permissions & Data Isolation

- All API endpoints require authentication
- Users see and manage only their own receipts, budgets, items, payments, and receipt-tags
- Categories and payment methods are global (shared)

---

## Validation Summary
- Positive amounts and quantities only
- No future dates for purchases/payments
- Budget end date ≥ start date
- Total price must equal quantity × unit price

---

## Troubleshooting
- 401 Unauthorized: Ensure you pass `Authorization: Token <token>`
- 403 Forbidden: You attempted to access or modify objects not owned by you
- 400 Bad Request: Check validation messages in the response
- DB errors: Verify your DB credentials in `settings.py`

Admin locked out (deactivated by mistake):
- Option A: `python manage.py shell` → set `is_active=True` (and optionally `is_staff=True`, `is_superuser=True`) for the admin, then save
- Option B: create a new superuser (`python manage.py createsuperuser`)

---

## Roadmap / Stretch Goals
- Roles: Admin vs Member
- File attachments for receipts (images/PDFs)
- Email notifications / reminders


