"""Unit tests for core views: dashboard, project lifecycle and AI generation endpoints."""

import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User

STATIC_OVERRIDE = override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'
)

from apps.core.models import (
    Project,
    NicheAnalysis,
    OfferStructure,
    RevenueStrategy,
    ProductOutline,
    CopyLibrary,
    AvatarProfile,
    ProjectArtifact,
    ChapterContent,
    PlanAEnrollment,
)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_user(username='testview', password='pass1234'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


def make_project(user, niche='Test niche for views', **kwargs):
    return Project.objects.create(user=user, niche_input=niche, **kwargs)


# ─────────────────────────────────────────────
# HomeView
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class HomeViewTests(TestCase):

    def test_home_renders_for_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_redirects_authenticated_to_dashboard(self):
        user = make_user('homeauth')
        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('core:dashboard'))


# ─────────────────────────────────────────────
# DashboardView
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class DashboardViewTests(TestCase):

    def setUp(self):
        self.user = make_user('dashuser')
        self.client.force_login(self.user)
        self.url = reverse('core:dashboard')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    def test_renders_dashboard_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_context_contains_required_keys(self):
        response = self.client.get(self.url)
        ctx = response.context
        self.assertIn('projects', ctx)
        self.assertIn('quickstart_steps', ctx)
        self.assertIn('primary_cta', ctx)
        self.assertIn('dashboard_stats', ctx)

    def test_shows_only_users_projects(self):
        other_user = make_user('otherusr')
        make_project(self.user, niche='My niche')
        make_project(other_user, niche='Other niche')
        response = self.client.get(self.url)
        projects = list(response.context['projects'])
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].niche_input, 'My niche')

    def test_quickstart_step_counts(self):
        PlanAEnrollment.objects.create(user=self.user, status='active')
        response = self.client.get(self.url)
        ctx = response.context
        self.assertEqual(len(ctx['quickstart_steps']), 3)

    def test_dashboard_stats_counts_projects(self):
        make_project(self.user, niche='p1')
        make_project(self.user, niche='p2')
        response = self.client.get(self.url)
        stats = response.context['dashboard_stats']
        self.assertEqual(stats['active_projects'], 2)


# ─────────────────────────────────────────────
# ProjectCreateView
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class ProjectCreateViewTests(TestCase):

    def setUp(self):
        self.user = make_user('createuser')
        self.client.force_login(self.user)
        self.url = reverse('core:project_create')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/project_create.html')

    def test_valid_post_creates_project_and_redirects(self):
        data = {
            'niche_input': 'Curso de finanzas para jóvenes',
            'brand_voice': 'mentor',
            'ai_model': 'gpt-4o',
            'primary_market': 'LATAM',
            'target_markets': ['LATAM'],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Project.objects.filter(user=self.user).count(), 1)
        project = Project.objects.get(user=self.user)
        self.assertRedirects(response, reverse('core:project_detail', kwargs={'pk': project.pk}))

    def test_valid_post_always_includes_primary_market_in_targets(self):
        data = {
            'niche_input': 'E-book cocina',
            'brand_voice': 'mentor',
            'ai_model': 'gpt-4o',
            'primary_market': 'MX',
            # target_markets deliberately omits primary
        }
        self.client.post(self.url, data)
        project = Project.objects.get(user=self.user)
        self.assertIn('MX', project.target_markets)

    def test_valid_post_updates_first_project_launched_at(self):
        enrollment = PlanAEnrollment.objects.create(user=self.user, status='active')
        data = {
            'niche_input': 'Test niche',
            'brand_voice': 'mentor',
            'ai_model': 'gpt-4o',
            'primary_market': 'LATAM',
            'target_markets': ['LATAM'],
        }
        self.client.post(self.url, data)
        enrollment.refresh_from_db()
        self.assertIsNotNone(enrollment.first_project_launched_at)

    def test_invalid_post_missing_niche(self):
        data = {
            'brand_voice': 'mentor',
            'ai_model': 'gpt-4o',
            'primary_market': 'LATAM',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.filter(user=self.user).count(), 0)


# ─────────────────────────────────────────────
# ProjectDetailView
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class ProjectDetailViewTests(TestCase):

    def setUp(self):
        self.user = make_user('detailuser')
        self.client.force_login(self.user)
        self.project = make_project(self.user)
        self.url = reverse('core:project_detail', kwargs={'pk': self.project.pk})

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/project_detail.html')

    def test_other_user_cannot_access_project(self):
        other = make_user('other_detail')
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_context_includes_step_flags(self):
        response = self.client.get(self.url)
        ctx = response.context
        self.assertIn('has_niche', ctx)
        self.assertIn('has_offer', ctx)
        self.assertIn('has_revenue', ctx)
        self.assertIn('has_outline', ctx)
        self.assertIn('has_copy', ctx)

    def test_next_step_recommends_niche_first(self):
        response = self.client.get(self.url)
        next_step = response.context['next_step']
        self.assertEqual(next_step['module'], 'niche')

    def test_next_step_recommends_offer_after_niche(self):
        NicheAnalysis.objects.create(project=self.project)
        response = self.client.get(self.url)
        next_step = response.context['next_step']
        self.assertEqual(next_step['module'], 'offer')

    def test_next_step_shows_factory_when_all_done(self):
        NicheAnalysis.objects.create(project=self.project)
        OfferStructure.objects.create(project=self.project)
        RevenueStrategy.objects.create(project=self.project)
        ProductOutline.objects.create(project=self.project)
        CopyLibrary.objects.create(project=self.project)
        response = self.client.get(self.url)
        next_step = response.context['next_step']
        self.assertEqual(next_step['action_type'], 'url')


# ─────────────────────────────────────────────
# ProjectDeleteView
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class ProjectDeleteViewTests(TestCase):

    def setUp(self):
        self.user = make_user('deleteuser')
        self.client.force_login(self.user)
        self.project = make_project(self.user)
        self.url = reverse('core:project_delete', kwargs={'pk': self.project.pk})

    def test_post_deletes_project_and_redirects(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('core:dashboard'))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_other_user_cannot_delete_project(self):
        other = make_user('other_delete')
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())


# ─────────────────────────────────────────────
# ProjectFactoryView
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class ProjectFactoryViewTests(TestCase):

    def setUp(self):
        self.user = make_user('factoryuser')
        self.client.force_login(self.user)
        self.project = make_project(self.user)
        self.url = reverse('core:project_factory', kwargs={'pk': self.project.pk})

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_renders_factory_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/project_factory.html')

    def test_other_user_cannot_access_factory(self):
        other = make_user('other_factory')
        self.client.force_login(other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


# ─────────────────────────────────────────────
# GenerateNicheView
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class GenerateNicheViewTests(TestCase):

    def setUp(self):
        self.user = make_user('nicheview')
        self.client.force_login(self.user)
        self.project = make_project(self.user)
        self.url = reverse('core:generate_niche', kwargs={'pk': self.project.pk})

    AI_DATA = {
        'avatar_name': 'Jóvenes emprendedores',
        'buyer_personas': [{'name': 'Juan'}],
        'pains': ['Falta de tiempo'],
        'desires': ['Independencia financiera'],
        'fears': ['Fracaso'],
        'barriers': ['Capital'],
        'product_names': ['Finanzas Para Todos'],
        'epiphany_bridge': 'Cuando descubrí X...',
        'raw_response': '{}',
    }

    @patch('apps.core.views.AIService')
    def test_post_creates_niche_analysis(self, MockAI):
        mock_service = MagicMock()
        mock_service.analyze_niche.return_value = self.AI_DATA
        MockAI.return_value = mock_service

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(NicheAnalysis.objects.filter(project=self.project).exists())

    @patch('apps.core.views.AIService')
    def test_post_sets_project_status_to_niche_done(self, MockAI):
        mock_service = MagicMock()
        mock_service.analyze_niche.return_value = self.AI_DATA
        MockAI.return_value = mock_service

        self.client.post(self.url)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'niche_done')

    @patch('apps.core.views.AIService')
    def test_post_auto_sets_title_from_product_names(self, MockAI):
        mock_service = MagicMock()
        mock_service.analyze_niche.return_value = self.AI_DATA
        MockAI.return_value = mock_service

        self.client.post(self.url)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Finanzas Para Todos')

    @patch('apps.core.views.AIService')
    def test_post_returns_error_on_ai_exception(self, MockAI):
        mock_service = MagicMock()
        mock_service.analyze_niche.side_effect = Exception('AI timeout')
        MockAI.return_value = mock_service

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_other_user_gets_404(self):
        other = make_user('other_niche')
        self.client.force_login(other)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)


# ─────────────────────────────────────────────
# GenerateFactoryArtifactView — invalid type
# ─────────────────────────────────────────────

@STATIC_OVERRIDE
class GenerateFactoryArtifactViewTests(TestCase):

    def setUp(self):
        self.user = make_user('factartuser')
        self.client.force_login(self.user)
        self.project = make_project(self.user)

    def test_invalid_artifact_type_returns_400(self):
        url = reverse('core:generate_factory_artifact', kwargs={
            'pk': self.project.pk,
            'artifact_type': 'invalid_type',
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_other_user_gets_404(self):
        other = make_user('other_art')
        self.client.force_login(other)
        url = reverse('core:generate_factory_artifact', kwargs={
            'pk': self.project.pk,
            'artifact_type': 'angles',
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
