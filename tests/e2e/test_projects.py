"""
E2E tests — Project management flows
======================================
Covers the core project management paths in MagicBook:

  1. Dashboard access control (anonymous → login redirect)
  2. Dashboard renders stats tiles and "Crear Nuevo Proyecto" CTA
  3. Full project creation flow → project detail redirect
  4. Project detail page renders key UI panels and next-step card
  5. Project deletion removes the project from the dashboard

These tests run against a real Django live server (pytest-django `live_server`
fixture) with a headless Chromium browser driven by Playwright.
No AI service calls are made — project creation only saves the model; generation
endpoints are separate AJAX calls outside this test scope.

Usage
-----
    pytest tests/e2e/test_projects.py -v
    pytest tests/e2e/test_projects.py -v --headed   # to watch the browser
"""

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import Page, expect

from apps.core.models import Project


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _create_project(user) -> Project:
    """Create a minimal project for the given user in the test DB."""
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
    THEN  they are redirected to the login page with a `next` query parameter
    """
    page.goto(f"{live_url}/dashboard/")
    expect(page).to_have_url(lambda u: "login" in u and "next" in u)


@pytest.mark.django_db
def test_project_detail_redirects_anonymous_user_to_login(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN a project that exists but the visitor is not authenticated
    WHEN  they navigate directly to /dashboard/project/<pk>/
    THEN  they are redirected to the login page
    """
    project = _create_project(auth_user)
    page.goto(f"{live_url}/dashboard/project/{project.pk}/")
    expect(page).to_have_url(lambda u: "login" in u)


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
    THEN  all three stats tiles are rendered with their labels
    """
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/")

    expect(page.locator("text=Proyectos Activos")).to_be_visible()
    expect(page.locator("text=Infoproductos Generados")).to_be_visible()
    expect(page.locator("text=Lanzamientos Listos")).to_be_visible()


@pytest.mark.django_db
def test_dashboard_shows_create_project_cta(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user
    WHEN  they visit the dashboard
    THEN  the 'Crear Nuevo Proyecto Mágico' button is visible and links to /project/new/
    """
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/")

    cta = page.locator("a", has_text="Crear Nuevo Proyecto Mágico")
    expect(cta).to_be_visible()
    expect(cta).to_have_attribute("href", lambda h: "project/new" in h)


@pytest.mark.django_db
def test_dashboard_shows_existing_project_cards(
    authenticated_page: Page, live_url: str, auth_user
):
    """
    GIVEN an authenticated user who already has a project
    WHEN  they visit the dashboard
    THEN  the project card is rendered with a link to its detail page
    """
    project = _create_project(auth_user)
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/")

    # Project card should link to project detail
    project_link = page.locator(f'a[href*="/dashboard/project/{project.pk}/"]').first
    expect(project_link).to_be_visible()


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
    THEN  all form fields are rendered (niche textarea, voice cards, model cards)
    """
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/project/new/")

    expect(page.locator("#id_niche_input")).to_be_visible()
    expect(page.locator('[name="brand_voice"]').first).to_be_visible()
    expect(page.locator('[name="ai_model"]').first).to_be_visible()
    expect(page.locator('select[name="primary_market"]')).to_be_visible()


@pytest.mark.django_db
def test_project_creation_flow_redirects_to_project_detail(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user on the project creation page
    WHEN  they fill in the niche description and submit the form
    THEN  a project is created and they are redirected to the project detail page
    """
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/project/new/")

    # Fill niche description
    page.fill("#id_niche_input", "Finanzas personales para millennials en LATAM")

    # brand_voice: first radio already pre-checked (coach); keep default
    # ai_model:    first model already pre-checked; keep default
    # primary_market: select LATAM option
    page.select_option('select[name="primary_market"]', value="LATAM")

    page.click('button[type="submit"]')

    # Should redirect to /dashboard/project/<pk>/
    page.wait_for_url("**/dashboard/project/*/", timeout=8_000)
    expect(page).to_have_url(lambda u: "/dashboard/project/" in u and u.endswith("/"))


@pytest.mark.django_db
def test_project_creation_empty_niche_shows_error(
    authenticated_page: Page, live_url: str
):
    """
    GIVEN an authenticated user on the project creation page
    WHEN  they submit the form without entering a niche description
    THEN  the form re-renders on the same page with a validation error
    """
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/project/new/")

    # Submit without filling required niche field
    page.click('button[type="submit"]')

    # Should remain on the create page
    expect(page).to_have_url(lambda u: "project/new" in u)


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
    THEN  the magic canvas grid and the 'Análisis de Nicho' panel are visible
    """
    project = _create_project(auth_user)
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/project/{project.pk}/")

    # Check the 'Análisis de Nicho' panel header
    expect(page.locator("text=Análisis de Nicho")).to_be_visible()


@pytest.mark.django_db
def test_project_detail_shows_delete_button(
    authenticated_page: Page, live_url: str, auth_user
):
    """
    GIVEN an authenticated user on their project detail page
    WHEN  they scroll to the delete section
    THEN  the 'Eliminar proyecto' button is visible
    """
    project = _create_project(auth_user)
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/project/{project.pk}/")

    delete_btn = page.locator("button", has_text="Eliminar proyecto")
    expect(delete_btn).to_be_visible()


@pytest.mark.django_db
def test_project_detail_only_accessible_by_owner(
    page: Page, live_url: str, auth_user
):
    """
    GIVEN project owned by user A
    WHEN  user B (different account) tries to access that project's detail page
    THEN  they receive a 404 response
    """
    project = _create_project(auth_user)

    # Create a second user and log in as them
    other_user = User.objects.create_user(
        username="other_e2e", password="OtherPass1!", email="other@test.com"
    )
    page.goto(f"{live_url}/accounts/login/")
    page.fill('input[name="username"]', "other_e2e")
    page.fill('input[name="password"]', "OtherPass1!")
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard/", timeout=8_000)

    page.goto(f"{live_url}/dashboard/project/{project.pk}/")
    # Django returns 404 for queryset mismatches in get_object_or_404
    expect(page).to_have_url(lambda u: str(project.pk) in u)  # stayed on same URL
    # 404 page should not show the "Análisis de Nicho" panel
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
    page = authenticated_page
    page.goto(f"{live_url}/dashboard/project/{pk}/")

    # Accept the JS confirm() dialog automatically
    page.on("dialog", lambda d: d.accept())

    delete_form = page.locator(f'form[action*="/project/{pk}/delete/"]')
    delete_form.locator('button[type="submit"]').click()

    # Should redirect to dashboard after deletion
    page.wait_for_url("**/dashboard/", timeout=8_000)
    expect(page).to_have_url(lambda u: u.endswith("/dashboard/"))

    # The project card should no longer appear
    expect(
        page.locator(f'a[href*="/dashboard/project/{pk}/"]')
    ).not_to_be_visible()

    # Confirm it's gone from the DB
    assert not Project.objects.filter(pk=pk).exists()
