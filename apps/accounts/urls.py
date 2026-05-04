"""URL routes for authentication, onboarding and billing actions."""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication lifecycle.
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Plan A onboarding and account actions.
    path('plan-a/onboarding/', views.PlanAOnboardingView.as_view(), name='plan_a_onboarding'),
    path('plan-a/resend-credentials/', views.PlanAResendCredentialsView.as_view(), name='plan_a_resend_credentials'),
    path('plan-a/upgrade/', views.PlanAUpgradeToPlanBView.as_view(), name='plan_a_upgrade'),
    path('plan-a/cancel/', views.PlanACancelView.as_view(), name='plan_a_cancel'),

    # Account profile page + logout.
    path('settings/', views.AccountSettingsView.as_view(), name='account_settings'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
