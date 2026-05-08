"""
Base Page Object
================
All page objects inherit from BasePage.  It wraps a Playwright ``Page``
instance and a live-server base URL, and exposes a single ``navigate()``
helper so subclasses only have to supply a relative path.

Design principles
-----------------
* Page objects do NOT contain assertions — that is the test's responsibility.
* Every locator is exposed as a ``@property`` so Playwright resolves it lazily
  at the moment it is needed (avoids stale-element issues).
* Action methods (fill, click, submit …) are kept intentionally thin; complex
  orchestration is left for test fixtures or the tests themselves.
"""

from playwright.sync_api import Page


class BasePage:
    """
    Shared base for all MagicBook page objects.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright browser page to drive.
    base_url : str
        Root URL of the running Django test server, e.g. ``http://localhost:54321``.
        Trailing slashes are stripped so subclasses can use ``/path`` patterns
        without worrying about double-slashes.
    """

    def __init__(self, page: Page, base_url: str) -> None:
        # Playwright Page instance — all browser interactions go through this
        self.page = page
        # Store without trailing slash so navigate("/path") always produces
        # exactly one slash between host and path
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str) -> None:
        """
        Navigate to ``path`` relative to the live-server root.

        Parameters
        ----------
        path : str
            Relative URL, e.g. ``"/accounts/login/"``.
        """
        self.page.goto(f"{self.base_url}{path}")
