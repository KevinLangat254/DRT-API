# DRT - Django Receipt Tracker

A Django-based application that provides both web views and API endpoints for a receipt tracking system. The codebase includes Django apps, templates, serializers, and tests.

## Project Layout

```

   DRT-API/
     ├─ manage.py
     ├─ receipt_tracker/        # Django project settings and root URLs
     ├─ DRT/                    # Main app with models, views, API, and templates
     │  ├─ models.py
     │  ├─ serializers.py
     │  ├─ views/
     │  ├─ templates/
     │  ├─ tests/
     │  └─ api_urls.py
     ├─ requirements.txt
     └─ ...
```

## Requirements

- Python 3.10+
- pip
- (Optional) virtualenv

All Python dependencies are listed in `DRT-API/requirements.txt`.

## Quick Start

### 1) Create and activate a virtual environment

Windows (PowerShell):
```powershell
cd C:\Users\User\Downloads\Drt2\DRT-API
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

macOS/Linux (bash/zsh):
```bash
cd ./DRT-API
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Apply database migrations
```bash
python manage.py migrate
```

### 4) Create a superuser (optional, for admin access)
```bash
python manage.py createsuperuser
```

### 5) Run the development server
```bash
python manage.py runserver
```

The site will be available at `http://127.0.0.1:8000/`.

- Admin: `http://127.0.0.1:8000/admin/`
- Web UI templates live under `DRT/templates/`
- API routes are organized in `DRT/api_urls.py` and included via project URLs

## Navigating Endpoints

Base URL in development: `http://127.0.0.1:8000/`

- Web (prefixed with `/drt/`):
  - Home: `GET /drt/`
  - Login: `GET/POST /drt/login/`
  - Register: `GET/POST /drt/register/`
  - Logout: `POST /drt/logout/`
  - Dashboard: `GET /drt/dashboard/`

- Admin:
  - Django Admin: `GET /admin/`

- API (prefixed with `/api/`):
  - Auth:
    - Obtain Token: `POST /api/auth/token/` (body: username, password)
    - Register: `POST /api/auth/register/`
    - Logout: `POST /api/auth/logout/` (requires token)
  - Resources (DRF router):
    - Users: `GET/POST /api/users/`, `GET/PATCH/DELETE /api/users/{id}/`
    - Categories: `GET/POST /api/categories/`, `GET/PATCH/DELETE /api/categories/{id}/`
    - Payment Methods: `GET/POST /api/payment-methods/`, `GET/PATCH/DELETE /api/payment-methods/{id}/`
    - Receipts: `GET/POST /api/receipts/`, `GET/PATCH/DELETE /api/receipts/{id}/`
    - Tags: `GET/POST /api/tags/`, `GET/PATCH/DELETE /api/tags/{id}/`
    - Receipt Tags: `GET/POST /api/receipt-tags/`, `GET/PATCH/DELETE /api/receipt-tags/{id}/`
    - Budgets: `GET/POST /api/budgets/`, `GET/PATCH/DELETE /api/budgets/{id}/`
    - Receipt Payments: `GET/POST /api/receipt-payments/`, `GET/PATCH/DELETE /api/receipt-payments/{id}/`
    - Receipt Items: `GET/POST /api/receipt-items/`, `GET/PATCH/DELETE /api/receipt-items/{id}/`

Example authenticated request with token:

```bash
curl -H "Authorization: Token <your_token>" http://127.0.0.1:8000/api/receipts/
```

## Running Tests

From the `DRT-API` directory with your virtual environment activated:
```bash
python manage.py test
```

## Configuration

By default, the project is configured to work with SQLite. For production or non-default setups, define environment variables and update `receipt_tracker/settings.py` as needed.

Common environment variables:
- `DJANGO_SECRET_KEY`: Secret key for Django
- `DJANGO_DEBUG`: `True` or `False`
- Database variables if switching from SQLite (e.g., `POSTGRES_*` or `DATABASE_URL`)

You can set environment variables in your shell before running Django commands.

## Code Structure Notes

- App code: `DRT/`
- Project settings: `DRT-API/receipt_tracker/settings.py`
- Root URLs: `DRT-API/receipt_tracker/urls.py`
- App URLs: `DRT/urls.py` and `DRT/api_urls.py`
- ASGI/WSGI entrypoints: `DRT-API/receipt_tracker/asgi.py`, `DRT-API/receipt_tracker/wsgi.py`

## Linting/Formatting

No specific linting or formatting configuration is included by default. You may add tools like `ruff`, `flake8`, or `black` as desired and include them in `requirements.txt`.

## Deployment

This repository includes ASGI and WSGI modules. For production:
- Set `DJANGO_DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use a proper database and static files storage
- Run behind a process manager (e.g., `gunicorn`/`uvicorn`) and a reverse proxy

## License

Add your preferred license here.
