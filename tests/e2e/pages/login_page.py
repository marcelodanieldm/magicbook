"""
Login Page Object
=================
Represents the Django login form at ``/accounts/login/``.

Encapsulates field locators and the composite ``login()`` convenience
method used by both the ``authenticated_page`` fixture in conftest.py
and individual login-flow tests.
"""

import re

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class LoginPage(BasePage):
    """Page object for the username / password login form."""

    PATH = "/accounts/login/"

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self) -> None:
        """Navigate to the login page."""
        self.navigate(self.PATH)

    # ── Field locators ────────────────────────────────────────────────────────

    @property
    def username_field(self) -> Locator:
        """The username text input."""
        return self.page.locator('input[name="username"]')

    @property
    def password_field(self) -> Locator:
        """The password text input."""
        return self.page.locator('input[name="password"]')

    @property
    def submit_button(self) -> Locator:
        """The form submit button."""
        return self.page.locator('button[type="submit"]')

    @property
    def error_message(self) -> Locator:
        """
        Inline error banner shown when credentials are invalid.

        The template renders the text "incorrectos" inside the error block.
        ``.first`` avoids strict-mode failures if the phrase appears in
        more than one DOM node (e.g. aria-label and visible text).
        """
        return self.page.locator("text=incorrectos").first

    # ── Actions ───────────────────────────────────────────────────────────────

    def fill_username(self, username: str) -> None:
        """Type ``username`` into the username field."""
        self.username_field.fill(username)

    def fill_password(self, password: str) -> None:
        """Type ``password`` into the password field."""
        self.password_field.fill(password)

    def submit(self) -> None:
        """Click the submit button."""
        self.submit_button.click()

    def login(self, username: str, password: str) -> None:
        """
        Complete the login form in a single call.

        Fills username and password then submits.  Does **not** wait for
        navigation — the caller is responsible for asserting the resulting
        URL (``page.wait_for_url(...)`` or ``expect(page).to_have_url(...)``).

        Parameters
        ----------
        username : str
            The account username.
        password : str
            The account password (plain text).
        """
        self.fill_username(username)
        self.fill_password(password)
        self.submit()
