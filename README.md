# 💰 BudgetingApp

A full-featured personal finance web application built with **Django**, designed to help users manage their budgets, track transactions, and set savings goals — all from a clean, unified dashboard.

---

## ✨ Features

- **Dashboard** — Overview of financial activity, budget status, and goal progress at a glance.
- **Transactions** — Log income and expense transactions with categories, payment methods, and optional notes. Link transactions directly to saving goals.
- **Budgets** — Create category-based spending budgets with date ranges and configurable alert thresholds. Visual status indicators (safe / warning / danger) update automatically.
- **Saving Goals** — Set financial goals with target amounts and deadlines. Contributions are tracked in real time with progress percentages and automatic completion detection.
- **User Accounts** — Email-based authentication using a custom `CustomUser` model. Supports registration, login, and profile management.
- **User Profiles** — Editable user profile linked to each account.
- **Auto-generated API Docs** — HTML documentation for all modules generated via `pdoc` (`generate_docs.py`).

---

## 🏗️ Project Structure

```
App/
├── BudgetingApp/          # Django project settings, URLs, WSGI/ASGI
├── budgets/               # Budget management app
├── dashboard/             # Dashboard overview app
├── saving_goals/          # Saving goals app (with Observer & Singleton patterns)
├── transactions/          # Transaction & category management app
├── users/                 # Custom user model and authentication
├── users_profile/         # User profile app
├── docs/api/              # Auto-generated HTML documentation
├── manage.py
└── requirements.txt
```

---

## 🎨 Design Patterns

The project intentionally demonstrates software design patterns:

- **Observer Pattern** (`saving_goals/observers.py`) — A `GoalManager` subject notifies attached observers (`NotificationObserver`, `DashboardUIObserver`) on events such as goal creation, contribution, and completion. This decouples event logic from side effects like Django messages.

- **Singleton Pattern** (`saving_goals/singleton.py`) — A `SessionManager` class uses `__new__` to ensure only one instance exists per process, providing a shared in-memory key-value session store.

- **Service Layer** — Business logic is separated from views into dedicated `services.py` modules in each app (budgets, transactions, saving_goals, users).

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 6.0 |
| Database | SQLite (default) |
| Frontend | Django Templates, HTML/CSS |
| Auth | Custom email-based user model |
| Timezone | Africa/Cairo |
| Docs | pdoc |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd "Software Project/App"

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Create a superuser (optional, for admin access)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`.

> **Note:** After login, users are redirected to `/dashboard/` by default.

---

## 🔐 Authentication

The app uses a **custom user model** (`users.CustomUser`) that authenticates via **email address** instead of a username.

- Register at `/users/signup/`
- Login at `/users/login/`
- After login, users are redirected to the dashboard

> ⚠️ Before deploying to production, replace the `SECRET_KEY` in `settings.py` with a secure value, set `DEBUG = False`, and configure `ALLOWED_HOSTS`.

---

## 📄 API Documentation

Auto-generated module documentation is available under `App/docs/api/`. Open `index.html` in your browser to browse it, or regenerate it with:

```bash
python generate_docs.py
```

---

## 👥 Authors

Developed as part of **CS251-2026 — Section 19**:

- Sara Hassan
- Student ID: 20242450
- Student ID: 20240093
- Student ID: 20240394
- Student ID: 20240150
