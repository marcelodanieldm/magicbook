"""
E2E test fixtures and shared helpers for MagicBook Playwright tests.

All E2E tests run against a real Django live server spawned by pytest-django's
`live_server` fixture.  Playwright drives a headless Chromium browser.

Fixture hierarchy
─────────────────
  live_server       (pytest-django)  – Django dev server on a free port
  live_url          (this file)      – resolves to live_server.url
  static_override   (autouse)        – swaps in simple static storage so the
                                       server doesn't require collectstatic
  auth_user         (this file)      – creates a DB user for auth tests
  authenticated_page (this file)     – Playwright page already logged in
"""

import os

# Allow Django synchronous DB operations when anyio/asyncio installs an event
# loop at session scope (required for pytest-playwright + pytest-django combo).
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import Page, expect

# ──────────────────────────────────────────────────────────────────────────────
# Django settings overrides
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def override_static(settings):
    """Replace Whitenoise ManifestStaticFilesStorage so collectstatic is not
    required when the live server serves test responses."""
    settings.STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    settings.EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"


# ──────────────────────────────────────────────────────────────────────────────
# URL helpers
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def live_url(live_server):
    """Return the root URL of the running test server, e.g. http://localhost:PORT."""
    return live_server.url


# ──────────────────────────────────────────────────────────────────────────────
# Auth helpers
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def auth_user(db):
    """Create and return a standard test user."""
    return User.objects.create_user(
        username="e2euser",
        password="E2ePassword1!",
        email="e2e@magicbook.test",
    )


@pytest.fixture()
def authenticated_page(page: Page, live_url: str, auth_user):
    """Return a Playwright page that has already completed the login flow."""
    page.goto(f"{live_url}/accounts/login/")
    page.fill('input[name="username"]', auth_user.username)
    page.fill('input[name="password"]', "E2ePassword1!")
    page.click('button[type="submit"]')
    # Wait until the dashboard is loaded after login redirect
    page.wait_for_url(f"**/dashboard/", timeout=8_000)
    return page
