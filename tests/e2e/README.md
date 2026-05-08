# MagicBook — E2E Tests (Playwright)

End-to-end tests that drive a real Chromium browser against a live Django server.
They verify the critical user-facing flows from the browser's perspective.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Running the Tests](#running-the-tests)
5. [Test Structure](#test-structure)
6. [Critical Flows Covered](#critical-flows-covered)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Tech Stack

| Library | Version | Role |
|---------|---------|------|
| `playwright` | ≥ 1.59 | Browser automation |
| `pytest-playwright` | ≥ 0.7 | pytest integration for Playwright |
| `pytest-django` | ≥ 4.12 | Django live server + DB fixtures |
| `pytest` | ≥ 9.0 | Test runner |

---

## Prerequisites

- Python virtualenv activated (`venv\Scripts\activate` on Windows).
- Dependencies installed (see below).
- No need to run `collectstatic` — the test `conftest.py` overrides Django's
  static file storage automatically.

---

## Setup

```bash
# 1. Install Python packages
pip install pytest pytest-django pytest-playwright playwright

# 2. Download the Chromium browser binary (one-time)
playwright install chromium
```

---

## Running the Tests

```bash
# Run all E2E tests (headless — default)
pytest tests/e2e/ -v

# Watch the browser while tests run
pytest tests/e2e/ -v --headed

# Run a single test file
pytest tests/e2e/test_auth.py -v

# Run a single test by name
pytest tests/e2e/test_auth.py::test_login_with_valid_credentials_redirects_to_dashboard -v

# Slow down each action by 500 ms (useful for debugging)
pytest tests/e2e/ -v --headed --slowmo 500

# Keep the browser open on failure (requires --headed)
pytest tests/e2e/ -v --headed --pause-on-failure
```

> **Tip:** Run unit tests separately (`pytest apps/`) to keep feedback loops fast.
> E2E tests start a real server and are slower by design.

---

## Test Structure

```
tests/
└── e2e/
    ├── conftest.py         ← Shared fixtures (live server URL, auth helpers,
    │                           settings overrides)
    ├── test_auth.py        ← Authentication flows (9 tests)
    ├── test_projects.py    ← Project management flows (10 tests)
    └── README.md           ← This file
```

### `conftest.py` — Shared Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `override_static` | function, autouse | Swaps Whitenoise compressed storage for simple storage so tests never require `collectstatic` |
| `base_url` | function | Root URL of the live Django test server |
| `auth_user` | function | Pre-created `User(username="e2euser")` in the test DB |
| `authenticated_page` | function | Playwright `Page` that has already logged in as `auth_user` |

---

## Critical Flows Covered

### `test_auth.py` — Authentication

| Test | What it verifies |
|------|-----------------|
| `test_home_page_renders_for_anonymous_user` | Landing page loads; hero title and CTA links are visible |
| `test_home_page_redirects_authenticated_user_to_dashboard` | Logged-in users visiting `/` are sent to `/dashboard/` |
| `test_registration_flow_redirects_to_onboarding` | Full 2-step registration (email → username+password) creates an account and redirects to `/accounts/plan-a/onboarding/` |
| `test_registration_with_mismatched_passwords_shows_error` | Form re-renders with a "contraseñas no coinciden" error when passwords differ |
| `test_authenticated_user_is_redirected_away_from_register` | Authenticated users are bounced away from `/accounts/register/` |
| `test_login_with_valid_credentials_redirects_to_dashboard` | Correct credentials → `/dashboard/` with stats tiles visible |
| `test_login_with_wrong_password_shows_error` | Wrong password → login page stays with "incorrectos" error |
| `test_login_with_nonexistent_user_shows_error` | Unknown username → same error message |
| `test_logout_terminates_session_and_redirects_to_home` | Logout form destroys the session; visiting `/dashboard/` afterwards redirects to login |
| `test_dashboard_redirects_anonymous_user_to_login` | Anonymous `GET /dashboard/` → redirect to login with `?next=/dashboard/` |

### `test_projects.py` — Project Management

| Test | What it verifies |
|------|-----------------|
| `test_dashboard_redirects_anonymous_user_to_login` | Anonymous visitors cannot access the dashboard |
| `test_project_detail_redirects_anonymous_user_to_login` | Anonymous visitors cannot access project detail pages |
| `test_dashboard_shows_three_stats_tiles` | "Proyectos Activos", "Infoproductos Generados", "Lanzamientos Listos" tiles all render |
| `test_dashboard_shows_create_project_cta` | "Crear Nuevo Proyecto Mágico" button is visible and links to `/project/new/` |
| `test_dashboard_shows_existing_project_cards` | An existing project card appears with a link to its detail page |
| `test_project_create_form_renders` | All form fields visible: niche textarea, brand-voice radios, AI-model radios, primary-market select |
| `test_project_creation_flow_redirects_to_project_detail` | Filling the form and submitting creates a `Project` row and redirects to `/dashboard/project/<pk>/` |
| `test_project_creation_empty_niche_shows_error` | Submitting without a niche description keeps the user on the create page |
| `test_project_detail_renders_canvas_and_next_step` | Project detail page shows the "Análisis de Nicho" panel |
| `test_project_detail_shows_delete_button` | The "Eliminar proyecto" button is rendered on the detail page |
| `test_project_detail_only_accessible_by_owner` | A different user cannot see another user's project (404) |
| `test_project_delete_removes_project_and_redirects_to_dashboard` | Confirming the delete dialog removes the project from the DB and the dashboard |

---

## Configuration

`pytest.ini` (project root) sets the Django settings module and test discovery
patterns so both unit tests and E2E tests can be run from the same `pytest`
invocation:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = magicbook.settings
python_files = tests_*.py test_*.py
python_classes = Test*
python_functions = test_*
```

**Key settings overridden at test time** (in `conftest.py`):

| Setting | Test value | Reason |
|---------|-----------|--------|
| `STATICFILES_STORAGE` | `django.contrib.staticfiles.storage.StaticFilesStorage` | Avoids `collectstatic` requirement |
| `EMAIL_BACKEND` | `django.core.mail.backends.dummy.EmailBackend` | Prevents real emails during registration tests |

---

## Troubleshooting

### `playwright install` must be run once

If you see `BrowserType.launch: Executable doesn't exist`, run:

```bash
playwright install chromium
```

### Static file errors (`ValueError: Missing staticfiles manifest entry`)

The `override_static` autouse fixture in `conftest.py` handles this. If you see
it in a new test that bypasses the fixture, add `settings` fixture usage to
override the storage.

### "Login page not found" or unexpected redirects

Make sure `DJANGO_SETTINGS_MODULE = magicbook.settings` is set in `pytest.ini`
and that the virtual environment is active when running `pytest`.

### Test isolation

Each test gets a fresh SQLite database (pytest-django's default). The
`live_server` fixture uses the same DB as the test. Fixtures like `auth_user`
create their own rows per test so there is no cross-test state leakage.
