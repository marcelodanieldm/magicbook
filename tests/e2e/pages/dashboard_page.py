"""
Dashboard Page Object
=====================
Represents the authenticated user dashboard at ``/dashboard/``.

Exposes the three KPI stats tiles, the "Crear Nuevo Proyecto Mágico" CTA,
project card links, and the logout form.
"""

import re

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class DashboardPage(BasePage):
    """Page object for the main project dashboard."""

    PATH = "/dashboard/"

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self) -> None:
        """Navigate to the dashboard."""
        self.navigate(self.PATH)

    # ── Stats tiles ───────────────────────────────────────────────────────────

    @property
    def active_projects_tile(self) -> Locator:
        """The 'Proyectos Activos' KPI stat tile."""
        return self.page.locator("text=Proyectos Activos")

    @property
    def generated_infoproducts_tile(self) -> Locator:
        """The 'Infoproductos Generados' KPI stat tile."""
        return self.page.locator("text=Infoproductos Generados")

    @property
    def ready_launches_tile(self) -> Locator:
        """The 'Lanzamientos Listos' KPI stat tile."""
        return self.page.locator("text=Lanzamientos Listos")

    # ── CTA ───────────────────────────────────────────────────────────────────

    @property
    def create_project_cta(self) -> Locator:
        """
        The 'Crear Nuevo Proyecto Mágico' anchor button.
        Its ``href`` must point to ``/dashboard/project/new/``.
        """
        return self.page.locator("a", has_text="Crear Nuevo Proyecto Mágico")

    def expect_cta_links_to_create(self) -> None:
        """Assert the CTA href matches the project-new URL pattern."""
        expect(self.create_project_cta).to_have_attribute(
            "href", re.compile(r"project/new")
        )

    # ── Project cards ─────────────────────────────────────────────────────────

    def project_card_link(self, pk: int) -> Locator:
        """
        Return the anchor element inside the project card for ``pk``.

        Uses ``.first`` to pick the primary card link when the card
        renders multiple anchors (e.g. title link + action buttons).
        """
        return self.page.locator(f'a[href*="/dashboard/project/{pk}/"]').first

    # ── Session ───────────────────────────────────────────────────────────────

    @property
    def logout_form(self) -> Locator:
        """
        The ``<form>`` element whose ``action`` points to Django's logout view.
        Submitting this form (POST) terminates the session.
        """
        return self.page.locator('form[action*="logout"]')

    def logout(self) -> None:
        """
        Click the logout submit button and wait for the page to load.

        After logout Django redirects to ``/`` (home page).  Callers
        should assert ``page.url`` or navigate elsewhere afterwards.
        """
        self.logout_form.locator('button[type="submit"]').click()
        # Wait for the redirect to complete before returning control
        self.page.wait_for_load_state("load")
