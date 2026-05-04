"""Account views for authentication, onboarding and plan management in MagicBook."""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from .forms import RegisterForm
from apps.core.models import PlanAEnrollment, PlanBEnrollment


# ---------------------------------------------------------------------------
# Transactional emails used by onboarding and plan events
# ---------------------------------------------------------------------------
def _send_plan_a_credentials_email(request, user):
    """Send Plan A welcome email with access links and credential reminder."""
    if not user.email:
        return False

    login_url = request.build_absolute_uri(reverse('accounts:login'))
    dashboard_url = request.build_absolute_uri(reverse('core:dashboard'))
    create_project_url = request.build_absolute_uri(reverse('core:project_create'))

    subject = 'Plan A activado: tus credenciales y acceso inmediato'
    message = (
        f'Hola {user.username},\n\n'
        'Tu compra del Plan A está activa.\n\n'
        'Paso 1) Recibes email con credenciales ✅\n'
        f'- Usuario: {user.username}\n'
        '- Contraseña: la que configuraste al registrarte\n'
        f'- Login: {login_url}\n\n'
        'Paso 2) Entras a la app al toque ✅\n'
        f'- Dashboard: {dashboard_url}\n\n'
        'Paso 3) Lanzas tu primer producto hoy ✅\n'
        f'- Crear proyecto: {create_project_url}\n\n'
        'Si olvidaste tu contraseña, usa recuperación desde la pantalla de login.\n\n'
        'Equipo MagicBook'
    )
    send_mail(subject, message, None, [user.email], fail_silently=False)
    return True


class LoginView(View):
    """Login endpoint that also tracks first-login milestone for Plan A."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, 'accounts/login.html')

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            enrollment, _ = PlanAEnrollment.objects.get_or_create(user=user)
            if enrollment.first_login_at is None:
                enrollment.first_login_at = timezone.now()
                enrollment.save(update_fields=['first_login_at', 'updated_at'])

            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        messages.error(request, 'Usuario o contraseña incorrectos.')
        return render(request, 'accounts/login.html', {'username': username})


class RegisterView(View):
    """Register user, activate Plan A and trigger onboarding email."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, 'accounts/register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            enrollment, _ = PlanAEnrollment.objects.get_or_create(user=user)
            enrollment.status = 'active'
            if enrollment.purchased_at is None:
                enrollment.purchased_at = timezone.now()
            if enrollment.first_login_at is None:
                enrollment.first_login_at = timezone.now()

            try:
                sent = _send_plan_a_credentials_email(request, user)
                if sent:
                    enrollment.credentials_email_sent_at = timezone.now()
            except Exception:
                # Keep onboarding flow even if email transport fails.
                pass

            enrollment.save()

            messages.success(request, f'¡Bienvenido a MagicBook, {user.username}!')
            return redirect('accounts:plan_a_onboarding')
        return render(request, 'accounts/register.html', {'form': form})


class LogoutView(View):
    """Session termination endpoint."""

    def post(self, request):
        logout(request)
        return redirect('home')


class PlanAOnboardingView(LoginRequiredMixin, View):
    """Shows the 3-step post-purchase Plan A flow and current completion state."""

    def get(self, request):
        enrollment, _ = PlanAEnrollment.objects.get_or_create(user=request.user)
        if enrollment.status != 'active':
            enrollment.status = 'active'
            if enrollment.purchased_at is None:
                enrollment.purchased_at = timezone.now()

        if enrollment.first_login_at is None:
            enrollment.first_login_at = timezone.now()

        if enrollment.credentials_email_sent_at is None:
            try:
                sent = _send_plan_a_credentials_email(request, request.user)
                if sent:
                    enrollment.credentials_email_sent_at = timezone.now()
            except Exception:
                pass

        enrollment.save()

        has_project = request.user.projects.exists()
        context = {
            'enrollment': enrollment,
            'step1_done': bool(enrollment.credentials_email_sent_at),
            'step2_done': bool(enrollment.first_login_at),
            'step3_done': bool(enrollment.first_project_launched_at or has_project),
            'has_project': has_project,
        }
        return render(request, 'accounts/plan_a_onboarding.html', context)


class PlanAResendCredentialsView(LoginRequiredMixin, View):
    """Resend Plan A credentials/access email."""

    def post(self, request):
        enrollment, _ = PlanAEnrollment.objects.get_or_create(user=request.user)
        try:
            sent = _send_plan_a_credentials_email(request, request.user)
            if sent:
                enrollment.credentials_email_sent_at = timezone.now()
                enrollment.save(update_fields=['credentials_email_sent_at', 'updated_at'])
                messages.success(request, 'Te reenviamos el email con tus credenciales y enlaces de acceso.')
            else:
                messages.error(request, 'No pudimos enviar el email porque tu cuenta no tiene un correo configurado.')
        except Exception as exc:
            messages.error(request, f'No se pudo reenviar el email: {exc}')

        return redirect('accounts:plan_a_onboarding')


# ---------------------------------------------------------------------------
# Account Settings
# ---------------------------------------------------------------------------

class AccountSettingsView(LoginRequiredMixin, View):
    """Shows current plan status, upgrade and cancellation options."""

    def get(self, request):
        plan_a = PlanAEnrollment.objects.filter(user=request.user).first()
        plan_b = PlanBEnrollment.objects.filter(user=request.user).first()
        context = {
            'plan_a': plan_a,
            'plan_b': plan_b,
        }
        return render(request, 'accounts/account_settings.html', context)


# ---------------------------------------------------------------------------
# Plan A → Plan B upgrade
# ---------------------------------------------------------------------------

def _send_plan_b_upgrade_email(request, user):
    """Send Plan B upgrade confirmation email."""
    if not user.email:
        return False
    dashboard_url = request.build_absolute_uri(reverse('core:dashboard'))
    subject = '¡Bienvenido a Plan B! Tu upgrade está activo'
    message = (
        f'Hola {user.username},\n\n'
        'Tu cuenta fue actualizada a Plan B con éxito.\n\n'
        'Ahora tenés acceso a:\n'
        '• 50 testeos simultáneos (vs 20 del Plan A)\n'
        '• Todas las funcionalidades del Plan A más acceso prioritario\n'
        '• Soporte prioritario por email\n\n'
        f'Ingresá a tu dashboard: {dashboard_url}\n\n'
        'Equipo MagicBook'
    )
    send_mail(subject, message, None, [user.email], fail_silently=False)
    return True


class PlanAUpgradeToPlanBView(LoginRequiredMixin, View):
    """Upgrade current user from Plan A to Plan B."""

    def post(self, request):
        plan_a = PlanAEnrollment.objects.filter(user=request.user, status='active').first()
        if not plan_a:
            messages.error(request, 'No tenés un Plan A activo para actualizar.')
            return redirect('accounts:account_settings')

        now = timezone.now()

        # Mark Plan A as upgraded
        plan_a.status = 'upgraded'
        plan_a.upgraded_at = now
        plan_a.save(update_fields=['status', 'upgraded_at', 'updated_at'])

        # Create (or reactivate) Plan B enrollment
        plan_b, _ = PlanBEnrollment.objects.get_or_create(user=request.user)
        plan_b.status = 'active'
        plan_b.upgraded_from_plan_a = True
        if plan_b.purchased_at is None:
            plan_b.purchased_at = now
        plan_b.save()

        # Upgrade all user projects to plan_b + raise concurrency limit
        request.user.projects.all().update(plan_tier='plan_b', max_simultaneous_tests=50)

        try:
            _send_plan_b_upgrade_email(request, request.user)
        except Exception:
            pass

        messages.success(request, '¡Tu cuenta fue actualizada a Plan B! Ahora tenés 50 testeos simultáneos.')
        return redirect('accounts:account_settings')


# ---------------------------------------------------------------------------
# Plan A cancellation
# ---------------------------------------------------------------------------

def _send_plan_a_cancellation_email(request, user):
    """Send Plan A cancellation confirmation email."""
    if not user.email:
        return False
    subject = 'Tu suscripción al Plan A fue cancelada'
    message = (
        f'Hola {user.username},\n\n'
        'Recibimos tu solicitud de cancelación del Plan A. Tu acceso continuará activo '
        'hasta el final del período facturado.\n\n'
        'Si tenés dudas o querés reactivar tu suscripción, respondé este email.\n\n'
        'Equipo MagicBook'
    )
    send_mail(subject, message, None, [user.email], fail_silently=False)
    return True


class PlanACancelView(LoginRequiredMixin, View):
    """Cancel the Plan A subscription for the current user."""

    def post(self, request):
        plan_a = PlanAEnrollment.objects.filter(user=request.user, status='active').first()
        if not plan_a:
            messages.error(request, 'No tenés un Plan A activo para cancelar.')
            return redirect('accounts:account_settings')

        cancel_reason = request.POST.get('cancel_reason', '').strip()
        now = timezone.now()

        plan_a.status = 'cancelled'
        plan_a.cancelled_at = now
        plan_a.cancel_reason = cancel_reason
        plan_a.save(update_fields=['status', 'cancelled_at', 'cancel_reason', 'updated_at'])

        try:
            _send_plan_a_cancellation_email(request, request.user)
        except Exception:
            pass

        messages.success(request, 'Tu suscripción al Plan A fue cancelada. Te enviamos un email de confirmación.')
        return redirect('accounts:account_settings')
