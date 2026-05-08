"""Unit tests for core models: Project, enrollment models and helper utilities."""

from django.test import TestCase
from django.contrib.auth.models import User

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
    ChapterRewriteHistory,
    PlanAEnrollment,
    PlanBEnrollment,
    WorkflowProject,
    ProjectStep,
)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_user(username='testuser', password='pass'):
    return User.objects.create_user(username=username, password=password)


def make_project(user, niche='Test niche', **kwargs):
    return Project.objects.create(user=user, niche_input=niche, **kwargs)


# ─────────────────────────────────────────────
# Project model
# ─────────────────────────────────────────────

class ProjectModelTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.project = make_project(self.user)

    def test_str_returns_title_when_set(self):
        self.project.title = 'My Title'
        self.project.save()
        self.assertEqual(str(self.project), 'My Title')

    def test_str_returns_niche_when_no_title(self):
        self.assertEqual(str(self.project), 'Test niche')

    def test_str_truncates_long_niche(self):
        long_niche = 'x' * 100
        project = make_project(self.user, niche=long_niche)
        self.assertEqual(str(project), long_niche[:60])

    def test_steps_completed_zero_initially(self):
        self.assertEqual(self.project.steps_completed, 0)

    def test_steps_completed_counts_niche(self):
        NicheAnalysis.objects.create(project=self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.steps_completed, 1)

    def test_steps_completed_counts_all_five(self):
        NicheAnalysis.objects.create(project=self.project)
        OfferStructure.objects.create(project=self.project)
        RevenueStrategy.objects.create(project=self.project)
        ProductOutline.objects.create(project=self.project)
        CopyLibrary.objects.create(project=self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.steps_completed, 5)

    def test_completion_percentage_zero(self):
        self.assertEqual(self.project.completion_percentage, 0)

    def test_completion_percentage_full(self):
        NicheAnalysis.objects.create(project=self.project)
        OfferStructure.objects.create(project=self.project)
        RevenueStrategy.objects.create(project=self.project)
        ProductOutline.objects.create(project=self.project)
        CopyLibrary.objects.create(project=self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.completion_percentage, 100)

    def test_default_status_is_draft(self):
        self.assertEqual(self.project.status, 'draft')

    def test_default_brand_voice_is_mentor(self):
        self.assertEqual(self.project.brand_voice, 'mentor')

    def test_default_ai_model_is_gpt4o(self):
        self.assertEqual(self.project.ai_model, 'gpt-4o')

    def test_ordering_newest_first(self):
        p1 = make_project(self.user, niche='first')
        p2 = make_project(self.user, niche='second')
        projects = list(Project.objects.filter(user=self.user))
        self.assertEqual(projects[0], p2)
        self.assertEqual(projects[1], p1)
        self.assertEqual(projects[2], self.project)


# ─────────────────────────────────────────────
# NicheAnalysis model
# ─────────────────────────────────────────────

class NicheAnalysisModelTests(TestCase):

    def setUp(self):
        self.user = make_user('nichemodel')
        self.project = make_project(self.user)

    def test_str_representation(self):
        niche = NicheAnalysis.objects.create(project=self.project)
        self.assertIn('Nicho', str(niche))

    def test_default_json_fields_are_lists(self):
        niche = NicheAnalysis.objects.create(project=self.project)
        self.assertIsInstance(niche.buyer_personas, list)
        self.assertIsInstance(niche.pains, list)
        self.assertIsInstance(niche.desires, list)
        self.assertIsInstance(niche.fears, list)
        self.assertIsInstance(niche.barriers, list)
        self.assertIsInstance(niche.product_names, list)


# ─────────────────────────────────────────────
# OfferStructure model
# ─────────────────────────────────────────────

class OfferStructureModelTests(TestCase):

    def setUp(self):
        self.user = make_user('offermodel')
        self.project = make_project(self.user)

    def test_str_representation(self):
        offer = OfferStructure.objects.create(project=self.project, product_name='Super Course')
        self.assertIn('Super Course', str(offer))

    def test_default_json_fields(self):
        offer = OfferStructure.objects.create(project=self.project)
        self.assertIsInstance(offer.price_points, list)
        self.assertIsInstance(offer.bonuses, list)
        self.assertIsInstance(offer.value_stack, list)
        self.assertIsInstance(offer.upsell, dict)
        self.assertIsInstance(offer.order_bump, dict)


# ─────────────────────────────────────────────
# ProjectArtifact model
# ─────────────────────────────────────────────

class ProjectArtifactModelTests(TestCase):

    def setUp(self):
        self.user = make_user('artifactmodel')
        self.project = make_project(self.user)

    def test_str_representation(self):
        artifact = ProjectArtifact.objects.create(
            project=self.project,
            artifact_type='angles',
            status='done',
        )
        self.assertIn('angles', str(artifact))

    def test_default_status_is_pending(self):
        artifact = ProjectArtifact.objects.create(
            project=self.project, artifact_type='angles'
        )
        self.assertEqual(artifact.status, 'pending')

    def test_unique_together_artifact_type_per_project(self):
        ProjectArtifact.objects.create(project=self.project, artifact_type='angles')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ProjectArtifact.objects.create(project=self.project, artifact_type='angles')


# ─────────────────────────────────────────────
# ChapterContent model
# ─────────────────────────────────────────────

class ChapterContentModelTests(TestCase):

    def setUp(self):
        self.user = make_user('chaptermodel')
        self.project = make_project(self.user)

    def test_str_representation(self):
        ch = ChapterContent.objects.create(
            project=self.project, chapter_number=1, title='Intro'
        )
        self.assertIn('1', str(ch))
        self.assertIn('Intro', str(ch))

    def test_default_status_is_pending(self):
        ch = ChapterContent.objects.create(project=self.project, chapter_number=1)
        self.assertEqual(ch.status, 'pending')

    def test_unique_chapter_per_project(self):
        ChapterContent.objects.create(project=self.project, chapter_number=1)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ChapterContent.objects.create(project=self.project, chapter_number=1)

    def test_ordering_by_chapter_number(self):
        ChapterContent.objects.create(project=self.project, chapter_number=3)
        ChapterContent.objects.create(project=self.project, chapter_number=1)
        ChapterContent.objects.create(project=self.project, chapter_number=2)
        nums = list(
            ChapterContent.objects.filter(project=self.project).values_list('chapter_number', flat=True)
        )
        self.assertEqual(nums, [1, 2, 3])


# ─────────────────────────────────────────────
# PlanAEnrollment model
# ─────────────────────────────────────────────

class PlanAEnrollmentModelTests(TestCase):

    def setUp(self):
        self.user = make_user('planmodel')

    def test_str_representation(self):
        enrollment = PlanAEnrollment.objects.create(user=self.user)
        self.assertIn('planmodel', str(enrollment))
        self.assertIn('PlanA', str(enrollment))

    def test_default_status_is_pending(self):
        enrollment = PlanAEnrollment.objects.create(user=self.user)
        self.assertEqual(enrollment.status, 'pending')

    def test_one_enrollment_per_user(self):
        PlanAEnrollment.objects.create(user=self.user)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            PlanAEnrollment.objects.create(user=self.user)


# ─────────────────────────────────────────────
# PlanBEnrollment model
# ─────────────────────────────────────────────

class PlanBEnrollmentModelTests(TestCase):

    def setUp(self):
        self.user = make_user('planbmodel')

    def test_str_representation(self):
        enrollment = PlanBEnrollment.objects.create(user=self.user)
        self.assertIn('PlanB', str(enrollment))

    def test_default_status_is_active(self):
        enrollment = PlanBEnrollment.objects.create(user=self.user)
        self.assertEqual(enrollment.status, 'active')


# ─────────────────────────────────────────────
# WorkflowProject model
# ─────────────────────────────────────────────

class WorkflowProjectModelTests(TestCase):

    def setUp(self):
        self.user = make_user('workflowmodel')

    def test_str_returns_title(self):
        wp = WorkflowProject.objects.create(user=self.user, title='My Workflow')
        self.assertEqual(str(wp), 'My Workflow')

    def test_default_status_is_draft(self):
        wp = WorkflowProject.objects.create(user=self.user, title='WP')
        self.assertEqual(wp.status, 'draft')

    def test_progress_percentage_default_zero(self):
        wp = WorkflowProject.objects.create(user=self.user, title='WP')
        self.assertEqual(wp.progress_percentage, 0)
