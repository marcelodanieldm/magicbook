"""
Project Create Page Object
==========================
Represents the new-project creation form at ``/dashboard/project/new/``.

Important: The submit button (``#create-project-submit``) starts **disabled**.
The JS function ``updateSubmitState()`` enables it only after the niche
textarea contains ≥ 24 characters.

Playwright's ``fill()`` method does not fire native browser ``input`` events,
so ``updateSubmitState()`` would never run.  The ``fill_niche()`` method
explicitly dispatches an ``"input"`` event after filling to work around this.
"""

from playwright.sync_api import Locator

from .base_page import BasePage


class ProjectCreatePage(BasePage):
    """Page object for the new-project form."""

    PATH = "/dashboard/project/new/"

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self) -> None:
        """Navigate to the project creation form."""
        self.navigate(self.PATH)

    # ── Field locators ────────────────────────────────────────────────────────

    @property
    def niche_textarea(self) -> Locator:
        """
        The niche-description ``<textarea>`` (``id="id_niche_input"``).
        Must contain ≥ 24 characters before the submit button is enabled.
        """
        return self.page.locator("#id_niche_input")

    @property
    def brand_voice_options(self) -> Locator:
        """All brand-voice radio-card ``<input>`` elements."""
        return self.page.locator('[name="brand_voice"]')

    @property
    def ai_model_options(self) -> Locator:
        """All AI-model radio-card ``<input>`` elements."""
        return self.page.locator('[name="ai_model"]')

    @property
    def primary_market_select(self) -> Locator:
        """The primary-market ``<select>`` dropdown."""
        return self.page.locator('select[name="primary_market"]')

    @property
    def submit_button(self) -> Locator:
        """
        The form submit button (``id="create-project-submit"``).
        Disabled by JS until the niche field has ≥ 24 characters.
        """
        return self.page.locator("#create-project-submit")

    # ── Actions ───────────────────────────────────────────────────────────────

    def fill_niche(self, text: str) -> None:
        """
        Fill the niche textarea and trigger the JS validator.

        Playwright's ``fill()`` does not fire native ``input`` events, so the
        JS ``updateSubmitState()`` function would not run and the submit button
        would remain disabled.  ``dispatch_event("input")`` simulates the
        event the browser normally fires on every keystroke.

        Parameters
        ----------
        text : str
            Niche description (must be ≥ 24 characters to enable the button).
        """
        self.niche_textarea.fill(text)
        # Trigger the JS listener that enables/disables the submit button
        self.niche_textarea.dispatch_event("input")

    def select_market(self, value: str) -> None:
        """
        Select a primary market by its ``<option value="...">`` attribute.

        Parameters
        ----------
        value : str
            Option value, e.g. ``"LATAM"``, ``"USA"``, ``"EU"``.
        """
        self.page.select_option('select[name="primary_market"]', value=value)

    def submit(self) -> None:
        """
        Click the submit button.

        Call ``fill_niche()`` first (and optionally assert
        ``not_to_be_disabled()`` on ``submit_button``) before invoking this.
        """
        self.submit_button.click()
