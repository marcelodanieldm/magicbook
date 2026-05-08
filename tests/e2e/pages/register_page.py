"""
Register Page Object
====================
Represents the 2-step user registration form at ``/accounts/register/``.

Step 1 — email field + ``#btn-step1`` button.
Step 2 — username / password / password_confirm fields revealed via JS
         after step 1 is submitted.

The ``register()`` composite method drives the full happy-path flow.
For error-case tests, each step's actions are also available individually.
"""

from playwright.sync_api import Locator

from .base_page import BasePage


class RegisterPage(BasePage):
    """Page object for the 2-step registration form."""

    PATH = "/accounts/register/"

    # ── Navigation ────────────────────────────────────────────────────────────

    def goto(self) -> None:
        """Navigate to the registration page."""
        self.navigate(self.PATH)

    # ── Step 1 locators & actions ─────────────────────────────────────────────

    @property
    def email_field(self) -> Locator:
        """The email text input shown in step 1."""
        return self.page.locator('input[name="email"]')

    def fill_email(self, email: str) -> None:
        """Type ``email`` into the step-1 email field."""
        self.email_field.fill(email)

    def submit_step1(self) -> None:
        """Click the 'Continue' button that transitions to step 2."""
        self.page.click("#btn-step1")

    # ── Step 2 locators & actions ─────────────────────────────────────────────

    def wait_for_step2(self) -> None:
        """
        Block until the JS transition reveals the step-2 username field.

        The form hides step-2 elements by default; they become visible after
        ``#btn-step1`` is clicked and the JS animation completes.
        """
        self.page.locator('input[name="username"]').wait_for(
            state="visible", timeout=4_000
        )

    @property
    def username_field(self) -> Locator:
        """The username text input shown in step 2."""
        return self.page.locator('input[name="username"]')

    def fill_username(self, username: str) -> None:
        """Type ``username`` into the step-2 username field."""
        self.page.fill('input[name="username"]', username)

    def fill_password(self, password: str) -> None:
        """Type ``password`` into the step-2 password field."""
        self.page.fill('input[name="password"]', password)

    def fill_password_confirm(self, password_confirm: str) -> None:
        """Type ``password_confirm`` into the step-2 confirmation field."""
        self.page.fill('input[name="password_confirm"]', password_confirm)

    def submit_step2(self) -> None:
        """Click the final submit button to create the account."""
        self.page.click('button[type="submit"]')

    # ── Composite helper ──────────────────────────────────────────────────────

    def register(
        self,
        email: str,
        username: str,
        password: str,
        password_confirm: str | None = None,
    ) -> None:
        """
        Drive the complete 2-step registration flow.

        Parameters
        ----------
        email : str
            New account e-mail address (step 1).
        username : str
            Desired username (step 2).
        password : str
            Desired password (step 2).
        password_confirm : str, optional
            Confirmation password (step 2).  Defaults to ``password`` for
            the happy-path; supply a different value to test mismatch errors.

        Note
        ----
        Does **not** wait for the post-submit redirect.  The caller decides
        what URL or element to assert next.
        """
        if password_confirm is None:
            password_confirm = password

        # ── Step 1: submit the email ──────────────────────────────────────────
        self.fill_email(email)
        self.submit_step1()

        # ── Step 2: fill credentials once the JS reveals them ────────────────
        self.wait_for_step2()
        self.fill_username(username)
        self.fill_password(password)
        self.fill_password_confirm(password_confirm)
        self.submit_step2()

    # ── Error locators ────────────────────────────────────────────────────────

    @property
    def password_mismatch_error(self) -> Locator:
        """Inline error shown when password and confirm-password do not match."""
        return self.page.locator("text=contraseñas no coinciden")
