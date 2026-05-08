"""
E2E tests — Authentication flows
=================================
Covers the most critical authentication paths in MagicBook:

  1. Home page renders correctly for anonymous visitors
  2. Full user registration (2-step form) → Plan A onboarding redirect
  3. Login with valid credentials → Dashboard
  4. Login with invalid credentials → inline error message
  5. Logout from an authenticated session → home page

These tests run against a real Django live server (pytest-django `live_server`
fixture) with a headless Chromium browser driven by Playwright.

Usage
-----
    pytest tests/e2e/test_auth.py -v
    pytest tests/e2e/test_auth.py -v --headed   # to see the browser
"""

import re

import pytest
from playwright.sync_api import Page, expect


# ──────────────────────────────────────────────────────────────────────────────
# 1. Landing page
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_home_page_renders_for_anonymous_user(page: Page, live_url: str):
    """
    GIVEN an anonymous visitor
    WHEN  they navigate to the root URL
    THEN  the landing page loads with the MagicBook hero title and CTA buttons
    """
    page.goto(live_url)

    # Title bar
    expect(page).to_have_title(re.compile("MagicBook"))

    # Both primary CTA buttons should be visible (es / en variants)
    ctas = page.locator("a[href*='register'], a[href*='login']")
    expect(ctas.first).to_be_visible()


@pytest.mark.django_db
def test_home_page_redirects_authenticated_user_to_dashboard(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a logged-in user
    WHEN  they navigate to the root URL
    THEN  they are redirected to the dashboard without seeing the landing page
    """
    # Log in first via the login page
    page.goto(f"{live_url}/accounts/login/")
    page.fill('input[name="username"]', auth_user.username)
    page.fill('input[name="password"]', "E2ePassword1!")
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard/", timeout=8_000)

    # Now hit root – should stay on dashboard
    page.goto(live_url)
    expect(page).to_have_url(re.compile(r"/dashboard/"))


# ──────────────────────────────────────────────────────────────────────────────
# 2. Registration flow
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_registration_flow_redirects_to_onboarding(page: Page, live_url: str):
    """
    GIVEN a new visitor
    WHEN  they complete the 2-step registration form
    THEN  an account is created and they are redirected to Plan A onboarding
    """
    page.goto(f"{live_url}/accounts/register/")

    # ── Step 1: email ─────────────────────────────────────────────────────────
    email_input = page.locator('input[name="email"]')
    expect(email_input).to_be_visible()
    email_input.fill("newuser@magicbook.test")

    page.click("#btn-step1")

    # ── Step 2: username + password ───────────────────────────────────────────
    # The JS transition moves to step2; wait for the username field to appear
    username_input = page.locator('input[name="username"]')
    username_input.wait_for(state="visible", timeout=4_000)

    username_input.fill("new_e2e_user")
    page.fill('input[name="password"]', "StrongPass123!")
    page.fill('input[name="password_confirm"]', "StrongPass123!")

    page.click('button[type="submit"]')

    # After successful registration, expect redirect to onboarding
    page.wait_for_url("**/accounts/plan-a/onboarding/**", timeout=8_000)
    expect(page).to_have_url(re.compile(r"plan-a/onboarding"))


@pytest.mark.django_db
def test_registration_with_mismatched_passwords_shows_error(
    page: Page, live_url: str
):
    """
    GIVEN a visitor on the register page
    WHEN  they submit mismatched passwords
    THEN  the form stays on the page and an error is shown
    """
    page.goto(f"{live_url}/accounts/register/")

    page.locator('input[name="email"]').fill("bad@magicbook.test")
    page.click("#btn-step1")

    page.locator('input[name="username"]').wait_for(state="visible", timeout=4_000)
    page.fill('input[name="username"]', "baduser")
    page.fill('input[name="password"]', "pass1234")
    page.fill('input[name="password_confirm"]', "different")
    page.click('button[type="submit"]')

    # Should remain on the register page (or re-render it)
    expect(page).to_have_url(re.compile(r"register|accounts"))
    # The error message is somewhere in the page body
    error = page.locator("text=contraseñas no coinciden")
    expect(error).to_be_visible()


@pytest.mark.django_db
def test_authenticated_user_is_redirected_away_from_register(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a logged-in user
    WHEN  they try to visit the register page
    THEN  they are redirected to the dashboard
    """
    page.goto(f"{live_url}/accounts/login/")
    page.fill('input[name="username"]', auth_user.username)
    page.fill('input[name="password"]', "E2ePassword1!")
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard/", timeout=8_000)

    page.goto(f"{live_url}/accounts/register/")
    expect(page).to_have_url(re.compile(r"/dashboard/"))


# ──────────────────────────────────────────────────────────────────────────────
# 3. Login flow
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_with_valid_credentials_redirects_to_dashboard(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a registered user
    WHEN  they log in with correct credentials
    THEN  they land on the dashboard and can see their project stats
    """
    page.goto(f"{live_url}/accounts/login/")

    expect(page.locator('input[name="username"]')).to_be_visible()
    page.fill('input[name="username"]', auth_user.username)
    page.fill('input[name="password"]', "E2ePassword1!")
    page.click('button[type="submit"]')

    page.wait_for_url("**/dashboard/", timeout=8_000)
    expect(page).to_have_url(re.compile(r"/dashboard/"))

    # Dashboard should show at least the "Proyectos Activos" stat tile
    expect(page.locator("text=Proyectos Activos")).to_be_visible()


@pytest.mark.django_db
def test_login_with_wrong_password_shows_error(page: Page, live_url: str, auth_user):
    """
    GIVEN a registered user
    WHEN  they submit an incorrect password
    THEN  they stay on the login page with an error message visible
    """
    page.goto(f"{live_url}/accounts/login/")
    page.fill('input[name="username"]', auth_user.username)
    page.fill('input[name="password"]', "wrong_password")
    page.click('button[type="submit"]')

    # Should remain on login page
    expect(page).to_have_url(re.compile(r"login"))

    # Error message contains "incorrectos"
    error_message = page.locator("text=incorrectos").first
    expect(error_message).to_be_visible()


@pytest.mark.django_db
def test_login_with_nonexistent_user_shows_error(page: Page, live_url: str, db):
    """
    GIVEN no user exists for the given username
    WHEN  a login attempt is made
    THEN  the error message is displayed on the login page
    """
    page.goto(f"{live_url}/accounts/login/")
    page.fill('input[name="username"]', "ghost_user")
    page.fill('input[name="password"]', "anything")
    page.click('button[type="submit"]')

    expect(page).to_have_url(re.compile(r"login"))
    expect(page.locator("text=incorrectos").first).to_be_visible()


# ──────────────────────────────────────────────────────────────────────────────
# 4. Logout flow
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_logout_terminates_session_and_redirects_to_home(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user on the dashboard
    WHEN  they click the logout button (POST to /accounts/logout/)
    THEN  the session is destroyed and they are sent to the home page
    """
    page = authenticated_page

    # Find and submit the logout form (POST form)
    logout_form = page.locator('form[action*="logout"]')
    expect(logout_form).to_be_visible()
    logout_form.locator('button[type="submit"]').click()

    # Should end up on the home page
    page.wait_for_load_state("load")
    assert page.url.rstrip("/") == live_url.rstrip("/")

    # Trying to visit dashboard should now redirect to login
    page.goto(f"{live_url}/dashboard/")
    expect(page).to_have_url(re.compile(r"login"))


# ──────────────────────────────────────────────────────────────────────────────
# 5. Dashboard access control
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_dashboard_redirects_anonymous_user_to_login(page: Page, live_url: str, db):
    """
    GIVEN an anonymous visitor
    WHEN  they attempt to access /dashboard/ directly
    THEN  they are redirected to the login page with a `next` parameter
    """
    page.goto(f"{live_url}/dashboard/")
    expect(page).to_have_url(re.compile(r"login.*next"))
