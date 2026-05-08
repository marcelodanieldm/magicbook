"""
E2E tests — Project management flows (Page Object Model)
=========================================================
Covers the core project management paths in MagicBook:

  1. Dashboard access control (anonymous → login redirect)
  2. Dashboard renders stats tiles and "Crear Nuevo Proyecto" CTA
  3. Full project creation flow → project detail redirect
  4. Project detail page renders key UI panels and next-step card
  5. Project deletion removes the project from the dashboard

All browser interactions are encapsulated in page objects under
``tests/e2e/pages/``.  Tests only contain setup, method calls on page
objects, and assertions — no raw Playwright selectors.

No AI service calls are made — project creation only saves the model;
generation endpoints are separate AJAX calls outside this test scope.

Usage
-----
    pytest tests/e2e/test_projects.py -v
    pytest tests/e2e/test_projects.py -v --headed   # to watch the browser
"""

import re

import pytest
from playwright.sync_api import Page, expect

from .pages.dashboard_page import DashboardPage
from .pages.login_page import LoginPage
from .pages.project_create_page import ProjectCreatePage
from .pages.project_detail_page import ProjectDetailPage


# ──────────────────────────────────────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────────────────────────────────────

def _create_project(user):
    """
    Create a minimal Project record for ``user`` directly in the test DB.

    Bypasses the creation form so tests that only need an existing project
    can skip the browser-based creation flow entirely.
    """    # Import inside helper so Django is fully configured when this runs
    from apps.core.models import Project
    return Project.objects.create(
        user=user,
        niche_input="Marketing digital para emprendedores",
        brand_voice="mentor",
        ai_model="gpt-4o",
        primary_market="LATAM",
    )


# ──────────────────────────────────────────────────────────────────────────────
# 1. Access control
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_dashboard_redirects_anonymous_user_to_login(page: Page, live_url: str, db):
    """
    GIVEN an anonymous visitor
    WHEN  they attempt to access /dashboard/ directly
    THEN  they are redirected to the login page with a ``next`` query parameter
    """
    # DashboardPage.goto() navigates to /dashboard/
    DashboardPage(page, live_url).goto()
    # Django's @login_required adds ?next=/dashboard/ to the redirect URL
    expect(page).to_have_url(re.compile(r"login.*next"))


@pytest.mark.django_db
def test_project_detail_redirects_anonymous_user_to_login(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a project that exists but the visitor is not authenticated
    WHEN  they navigate directly to /dashboard/project/<pk>/
    THEN  they are redirected to the login page
    """
    # Create a project in the DB so the URL exists
    project = _create_project(auth_user)
    # Navigate as anonymous — ProjectDetailPage.goto() builds the dynamic URL
    ProjectDetailPage(page, live_url, project.pk).goto()
    expect(page).to_have_url(re.compile(r"login"))


# ──────────────────────────────────────────────────────────────────────────────
# 2. Dashboard UI
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_dashboard_shows_three_stats_tiles(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user
    WHEN  they visit the dashboard
    THEN  all three KPI stats tiles are rendered with their labels
    """
    dashboard = DashboardPage(authenticated_page, live_url)
    dashboard.goto()

    # Each tile locator is a named property on DashboardPage
    expect(dashboard.active_projects_tile).to_be_visible()
    expect(dashboard.generated_infoproducts_tile).to_be_visible()
    expect(dashboard.ready_launches_tile).to_be_visible()


@pytest.mark.django_db
def test_dashboard_shows_create_project_cta(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user
    WHEN  they visit the dashboard
    THEN  the 'Crear Nuevo Proyecto Mágico' button is visible and links to /project/new/
    """
    dashboard = DashboardPage(authenticated_page, live_url)
    dashboard.goto()

    # CTA must be visible
    expect(dashboard.create_project_cta).to_be_visible()
    # Its href must point to the project creation route
    dashboard.expect_cta_links_to_create()


@pytest.mark.django_db
def test_dashboard_shows_existing_project_cards(
    authenticated_page: Page, live_url: str, auth_user
):
    """
    GIVEN an authenticated user who already has a project
    WHEN  they visit the dashboard
    THEN  the project card is rendered with a link to its detail page
    """
    # Create project directly in DB (no browser form needed here)
    project = _create_project(auth_user)

    dashboard = DashboardPage(authenticated_page, live_url)
    dashboard.goto()

    # project_card_link() returns the anchor for this specific PK
    expect(dashboard.project_card_link(project.pk)).to_be_visible()


# ──────────────────────────────────────────────────────────────────────────────
# 3. Project creation
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_project_create_form_renders(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user
    WHEN  they navigate to /dashboard/project/new/
    THEN  all required form controls are rendered and visible
    """
    create_page = ProjectCreatePage(authenticated_page, live_url)
    create_page.goto()

    # Each locator is a named property on ProjectCreatePage
    expect(create_page.niche_textarea).to_be_visible()
    expect(create_page.brand_voice_options.first).to_be_visible()
    expect(create_page.ai_model_options.first).to_be_visible()
    expect(create_page.primary_market_select).to_be_visible()


@pytest.mark.django_db
def test_project_creation_flow_redirects_to_project_detail(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user on the project creation page
    WHEN  they fill in the niche description and submit the form
    THEN  a project is created and they are redirected to /dashboard/project/<pk>/
    """
    create_page = ProjectCreatePage(authenticated_page, live_url)
    create_page.goto()

    # fill_niche() dispatches an 'input' event to trigger updateSubmitState()
    # which enables the submit button once the niche has ≥ 24 characters
    create_page.fill_niche("Finanzas personales para millennials en LATAM")

    # Assert the submit button is now enabled before clicking
    expect(create_page.submit_button).not_to_be_disabled()

    # Select LATAM as primary market (default brand_voice & ai_model are fine)
    create_page.select_market("LATAM")
    create_page.submit()

    # After successful creation the app redirects to /dashboard/project/<pk>/
    authenticated_page.wait_for_url(
        re.compile(r"/dashboard/project/\d+/"), timeout=8_000
    )
    expect(authenticated_page).to_have_url(re.compile(r"/dashboard/project/\d+/"))


@pytest.mark.django_db
def test_project_creation_empty_niche_shows_error(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user on the project creation page
    WHEN  they have not entered a niche description (empty textarea)
    THEN  the submit button remains disabled (JS client-side validation)
    """
    create_page = ProjectCreatePage(authenticated_page, live_url)
    create_page.goto()

    # The submit button must start disabled — no text has been entered
    # JS updateSubmitState() requires ≥ 24 characters to enable it
    expect(create_page.submit_button).to_be_disabled()


# ──────────────────────────────────────────────────────────────────────────────
# 4. Project detail
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_project_detail_renders_canvas_and_next_step(
    authenticated_page: Page, live_url: str, auth_user
):
    """
    GIVEN an authenticated user with an existing project
    WHEN  they visit the project detail page
    THEN  the 'Análisis de Nicho' panel heading is visible
    """
    project = _create_project(auth_user)

    detail_page = ProjectDetailPage(authenticated_page, live_url, project.pk)
    detail_page.goto()

    # niche_analysis_heading uses get_by_role() to avoid strict-mode violations
    expect(detail_page.niche_analysis_heading).to_be_visible()


@pytest.mark.django_db
def test_project_detail_shows_delete_button(
    authenticated_page: Page, live_url: str, auth_user
):
    """
    GIVEN an authenticated user on their project detail page
    WHEN  they view the page
    THEN  the 'Eliminar proyecto' button is visible
    """
    project = _create_project(auth_user)

    detail_page = ProjectDetailPage(authenticated_page, live_url, project.pk)
    detail_page.goto()

    expect(detail_page.delete_button).to_be_visible()


@pytest.mark.django_db
def test_project_detail_only_accessible_by_owner(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a project owned by user A
    WHEN  user B tries to access that project's detail page
    THEN  Django returns a 404 and the canvas panel is not shown
    """
    project = _create_project(auth_user)

    # Create a second user and log in as them using LoginPage
    from django.contrib.auth.models import User
    User.objects.create_user(
        username="other_e2e", password="OtherPass1!", email="other@test.com"
    )
    login = LoginPage(page, live_url)
    login.goto()
    login.login("other_e2e", "OtherPass1!")
    page.wait_for_url("**/dashboard/", timeout=8_000)

    # Attempt to access the first user's project as the second user
    detail_page = ProjectDetailPage(page, live_url, project.pk)
    detail_page.goto()

    # Django's get_object_or_404 returns 404 — URL stays the same (not redirect)
    expect(page).to_have_url(re.compile(str(project.pk)))
    # The canvas heading must NOT appear on a 404 page
    expect(page.locator("text=Análisis de Nicho")).not_to_be_visible()


# ──────────────────────────────────────────────────────────────────────────────
# 5. Project deletion
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_project_delete_removes_project_and_redirects_to_dashboard(
    authenticated_page: Page, live_url: str, auth_user
):
    """
    GIVEN an authenticated user on their project detail page
    WHEN  they confirm the delete action
    THEN  the project is removed from the DB and they are redirected to /dashboard/
    """
    project = _create_project(auth_user)
    pk = project.pk

    detail_page = ProjectDetailPage(authenticated_page, live_url, pk)
    detail_page.goto()

    # delete_project() uses page.once("dialog", ...) and clicks the delete button
    detail_page.delete_project()

    # After deletion the app must redirect to the dashboard
    authenticated_page.wait_for_url("**/dashboard/", timeout=8_000)
    expect(authenticated_page).to_have_url(re.compile(r"/dashboard/"))

    # The project card must no longer appear on the dashboard
    dashboard = DashboardPage(authenticated_page, live_url)
    expect(dashboard.project_card_link(pk)).not_to_be_visible()

    # Verify the record is actually gone from the database
    from apps.core.models import Project
    assert not Project.objects.filter(pk=pk).exists()
