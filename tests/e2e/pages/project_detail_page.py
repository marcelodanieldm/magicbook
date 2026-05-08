"""
Project Detail Page Object
===========================
Represents an individual project's canvas / detail page at
``/dashboard/project/<pk>/``.

Unlike other page objects, this one is instantiated with a project primary
key because the URL is dynamic.  The PK is stored as ``self.pk`` and used
in URL construction and delete-form selectors.
"""

from playwright.sync_api import Locator

from .base_page import BasePage


class ProjectDetailPage(BasePage):
    """
    Page object for the project detail / magic-canvas view.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright browser page to drive.
    base_url : str
        Root URL of the running Django test server.
    pk : int
        Primary key of the project being viewed.
    """

    def __init__(self, page, base_url: str, pk: int) -> None:
        super().__init__(page, base_url)
        # Primary key of the project — included in URLs and form selectors
        self.pk = pk

    @property
    def path(self) -> str:
        """Relative URL for this project's detail page."""
        return f"/dashboard/project/{self.pk}/"

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self) -> None:
        """Navigate to this project's detail page."""
        self.navigate(self.path)

    # ── Content locators ──────────────────────────────────────────────────────

    @property
    def niche_analysis_heading(self) -> Locator:
        """
        The 'Análisis de Nicho' section heading element.

        Uses ``get_by_role("heading")`` instead of a text locator to avoid
        strict-mode violations — the text may appear in multiple nodes (e.g.
        a visible heading AND a hidden data-attribute or aria-label).
        """
        return self.page.get_by_role("heading", name="Análisis de Nicho")

    @property
    def delete_button(self) -> Locator:
        """The 'Eliminar proyecto' ``<button>`` inside the delete form."""
        return self.page.locator("button", has_text="Eliminar proyecto")

    @property
    def delete_form(self) -> Locator:
        """
        The ``<form>`` whose ``action`` points to the project delete endpoint
        (``/dashboard/project/<pk>/delete/``).
        """
        return self.page.locator(f'form[action*="/project/{self.pk}/delete/"]')

    # ── Actions ───────────────────────────────────────────────────────────────

    def delete_project(self) -> None:
        """
        Accept the browser ``confirm()`` dialog and click 'Eliminar proyecto'.

        Uses ``page.once("dialog", ...)`` so the handler fires exactly once
        for this confirmation dialog, avoiding interference with any other
        dialogs that might appear in the same test session.
        After this call the caller should wait for the redirect to ``/dashboard/``.
        """
        # Register a one-time dialog handler BEFORE the click triggers the dialog
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.delete_form.locator('button[type="submit"]').click()
