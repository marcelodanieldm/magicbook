"""
Home Page Object
================
Represents the public landing page at ``/``.

This is the first screen anonymous visitors see.  It contains hero text,
CTA buttons that link to /register/ and /login/, and the site <title>.
"""

import re

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class HomePage(BasePage):
    """Page object for the MagicBook public landing page."""

    # Relative URL for this screen
    PATH = "/"

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self) -> None:
        """Navigate to the home page."""
        self.navigate(self.PATH)

    # ── Assertions ───────────────────────────────────────────────────────────

    def expect_title_contains(self, text: str) -> None:
        """Assert that the page ``<title>`` element contains ``text``."""
        # to_have_title() requires a string or re.compile() — never a lambda
        expect(self.page).to_have_title(re.compile(text))

    # ── Locators ─────────────────────────────────────────────────────────────

    @property
    def cta_links(self) -> Locator:
        """
        All anchor elements that link to the register or login routes.
        The landing page contains both guest-only CTA buttons; checking
        ``.first`` is enough to assert at least one is visible.
        """
        return self.page.locator("a[href*='register'], a[href*='login']")
