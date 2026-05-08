"""
Page Object Model (POM) package for MagicBook E2E tests.

Each module exposes a single page object class that encapsulates all
selectors and actions for one route/screen.  Test files import the
classes they need and interact with the app exclusively through them,
keeping low-level Playwright calls out of the test body.

Classes
-------
BasePage          — shared base with navigate() helper
HomePage          — /
LoginPage         — /accounts/login/
RegisterPage      — /accounts/register/
DashboardPage     — /dashboard/
ProjectCreatePage — /dashboard/project/new/
ProjectDetailPage — /dashboard/project/<pk>/
"""

from .base_page import BasePage
from .home_page import HomePage
from .login_page import LoginPage
from .register_page import RegisterPage
from .dashboard_page import DashboardPage
from .project_create_page import ProjectCreatePage
from .project_detail_page import ProjectDetailPage

__all__ = [
    "BasePage",
    "HomePage",
    "LoginPage",
    "RegisterPage",
    "DashboardPage",
    "ProjectCreatePage",
    "ProjectDetailPage",
]
