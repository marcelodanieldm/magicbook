"""
E2E tests — Authentication flows (Page Object Model)
=====================================================
Covers the most critical authentication paths in MagicBook:

  1. Home page renders correctly for anonymous visitors
  2. Full user registration (2-step form) → Plan A onboarding redirect
  3. Login with valid credentials → Dashboard
  4. Login with invalid credentials → inline error message
  5. Logout from an authenticated session → home page

All browser interactions are encapsulated in page objects under
``tests/e2e/pages/``.  Tests only contain setup, method calls on page
objects, and assertions — no raw Playwright selectors.

Usage
-----
    pytest tests/e2e/test_auth.py -v
    pytest tests/e2e/test_auth.py -v --headed   # to see the browser
"""

import re

import pytest
from playwright.sync_api import Page, expect

from .pages.home_page import HomePage
from .pages.login_page import LoginPage
from .pages.register_page import RegisterPage
from .pages.dashboard_page import DashboardPage


# ──────────────────────────────────────────────────────────────────────────────
# 1. Landing page
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_home_page_renders_for_anonymous_user(page: Page, live_url: str):
    """
    GIVEN an anonymous visitor
    WHEN  they navigate to the root URL
    THEN  the landing page loads with the MagicBook title and CTA buttons
    """
    home = HomePage(page, live_url)
    home.goto()

    # Page <title> must contain "MagicBook"
    home.expect_title_contains("MagicBook")

    # At least one link pointing to /register/ or /login/ must be visible
    expect(home.cta_links.first).to_be_visible()


@pytest.mark.django_db
def test_home_page_redirects_authenticated_user_to_dashboard(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a logged-in user
    WHEN  they navigate to the root URL
    THEN  they are redirected to the dashboard without seeing the landing page
    """
    # Log in via the login page object
    login = LoginPage(page, live_url)
    login.goto()
    login.login(auth_user.username, "E2ePassword1!")
    page.wait_for_url("**/dashboard/", timeout=8_000)

    # Visiting root while authenticated should stay on /dashboard/
    HomePage(page, live_url).goto()
    expect(page).to_have_url(re.compile(r"/dashboard/"))


# ──────────────────────────────────────────────────────────────────────────────
# 2. Registration flow
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_registration_flow_redirects_to_onboarding(page: Page, live_url: str):
    """
    GIVEN a new visitor
    WHEN  they complete the 2-step registration form with valid data
    THEN  an account is created and they are redirected to Plan A onboarding
    """
    register = RegisterPage(page, live_url)
    register.goto()

    # register() drives both step-1 (email) and step-2 (username/password)
    register.register(
        email="newuser@magicbook.test",
        username="new_e2e_user",
        password="StrongPass123!",
    )

    # Successful registration must redirect to onboarding
    page.wait_for_url("**/accounts/plan-a/onboarding/**", timeout=8_000)
    expect(page).to_have_url(re.compile(r"plan-a/onboarding"))


@pytest.mark.django_db
def test_registration_with_mismatched_passwords_shows_error(
    page: Page, live_url: str
):
    """
    GIVEN a visitor on the register page
    WHEN  they submit mismatched passwords in step 2
    THEN  the form stays on the page and a mismatch error is shown
    """
    register = RegisterPage(page, live_url)
    register.goto()

    # Pass an intentionally different password_confirm to trigger the error
    register.register(
        email="bad@magicbook.test",
        username="baduser",
        password="pass1234",
        password_confirm="different",
    )

    # Should remain on the register/accounts URL (not redirected)
    expect(page).to_have_url(re.compile(r"register|accounts"))
    # The inline mismatch error must be visible
    expect(register.password_mismatch_error).to_be_visible()


@pytest.mark.django_db
def test_authenticated_user_is_redirected_away_from_register(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a logged-in user
    WHEN  they try to visit the register page
    THEN  they are redirected back to the dashboard
    """
    # Log in first
    login = LoginPage(page, live_url)
    login.goto()
    login.login(auth_user.username, "E2ePassword1!")
    page.wait_for_url("**/dashboard/", timeout=8_000)

    # Attempting to visit /register/ while authenticated should redirect
    RegisterPage(page, live_url).goto()
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
    THEN  they land on the dashboard and can see the 'Proyectos Activos' tile
    """
    login = LoginPage(page, live_url)
    login.goto()

    # Username field must be visible before interacting
    expect(login.username_field).to_be_visible()

    login.login(auth_user.username, "E2ePassword1!")
    page.wait_for_url("**/dashboard/", timeout=8_000)
    expect(page).to_have_url(re.compile(r"/dashboard/"))

    # At least one dashboard stats tile must be rendered
    dashboard = DashboardPage(page, live_url)
    expect(dashboard.active_projects_tile).to_be_visible()


@pytest.mark.django_db
def test_login_with_wrong_password_shows_error(page: Page, live_url: str, auth_user):
    """
    GIVEN a registered user
    WHEN  they submit an incorrect password
    THEN  they stay on the login page with the 'incorrectos' error visible
    """
    login = LoginPage(page, live_url)
    login.goto()
    login.login(auth_user.username, "wrong_password")

    # Must remain on the login page
    expect(page).to_have_url(re.compile(r"login"))
    # Error message provided by the LoginPage page object
    expect(login.error_message).to_be_visible()


@pytest.mark.django_db
def test_login_with_nonexistent_user_shows_error(page: Page, live_url: str, db):
    """
    GIVEN no user exists for the given username
    WHEN  a login attempt is made
    THEN  the 'incorrectos' error message is displayed on the login page
    """
    login = LoginPage(page, live_url)
    login.goto()
    login.login("ghost_user", "anything")

    expect(page).to_have_url(re.compile(r"login"))
    expect(login.error_message).to_be_visible()


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
    # DashboardPage.logout() clicks the logout form and waits for load
    dashboard = DashboardPage(authenticated_page, live_url)
    dashboard.logout()

    # After logout the app must redirect to the root URL
    assert authenticated_page.url.rstrip("/") == live_url.rstrip("/")

    # A subsequent visit to /dashboard/ must now redirect to login
    dashboard.goto()
    expect(authenticated_page).to_have_url(re.compile(r"login"))


# ──────────────────────────────────────────────────────────────────────────────
# 5. Dashboard access control
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_dashboard_redirects_anonymous_user_to_login(page: Page, live_url: str, db):
    """
    GIVEN an anonymous visitor
    WHEN  they attempt to access /dashboard/ directly
    THEN  they are redirected to the login page with a ``next`` query parameter
    """
    DashboardPage(page, live_url).goto()
    # Django's @login_required redirects to /accounts/login/?next=/dashboard/
    expect(page).to_have_url(re.compile(r"login.*next"))
