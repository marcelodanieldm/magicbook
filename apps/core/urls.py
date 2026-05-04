"""Core routes for dashboard pages and AI-powered API endpoints."""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main dashboard and project lifecycle pages.
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('project/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/factory/', views.ProjectFactoryView.as_view(), name='project_factory'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # AI Generation endpoints — modular (step by step)
    path('api/generate/niche/<int:pk>/', views.GenerateNicheView.as_view(), name='generate_niche'),
    path('api/generate/offer/<int:pk>/', views.GenerateOfferView.as_view(), name='generate_offer'),
    path('api/generate/avatars/<int:pk>/', views.GenerateAvatarsView.as_view(), name='generate_avatars'),
    path('api/generate/revenue/<int:pk>/', views.GenerateRevenueView.as_view(), name='generate_revenue'),
    path('api/generate/outline/<int:pk>/', views.GenerateOutlineView.as_view(), name='generate_outline'),
    path('api/generate/copy/<int:pk>/', views.GenerateCopyView.as_view(), name='generate_copy'),

    # AI Generation endpoint — unified (all 4 modules, single call)
    path('api/generate/all/<int:pk>/', views.GenerateAllView.as_view(), name='generate_all'),

    # Fábrica 16 artifact generation and artifact detail views.
    path('api/generate/factory/<int:pk>/<str:artifact_type>/', views.GenerateFactoryArtifactView.as_view(), name='generate_factory_artifact'),
    path('api/artifact/<int:pk>/<str:artifact_type>/detail/', views.ArtifactDetailView.as_view(), name='artifact_detail'),
    path('api/plan-a/test-run/<int:pk>/start/', views.StartPlanATestRunView.as_view(), name='start_plan_a_test_run'),

    # Chapter Writer — Fase 2 (one chapter per call)
    path('api/write/chapter/<int:pk>/<int:chapter_num>/', views.WriteChapterView.as_view(), name='write_chapter'),
    path('api/rewrite/paragraph/<int:pk>/', views.RewriteParagraphView.as_view(), name='rewrite_paragraph'),
    path('api/rewrite/chapter/<int:pk>/', views.RewriteChapterView.as_view(), name='rewrite_chapter'),
    path('api/rewrite/chapter/<int:pk>/undo/', views.UndoChapterRewriteView.as_view(), name='undo_rewrite_chapter'),

    # Chapter Writer — Fábrica (write ALL chapters sequentially, SSE stream)
    path('api/write/all-chapters/<int:pk>/', views.WriteAllChaptersView.as_view(), name='write_all_chapters'),

    # Download assembled E-book as Markdown
    path('api/download/ebook/<int:pk>/', views.DownloadEbookView.as_view(), name='download_ebook'),

    # Book Content — Step 12 professional editor (save/load/AI-enhance)
    path('api/book-content/<int:pk>/save/', views.BookContentSaveView.as_view(), name='book_content_save'),
    path('api/book-content/<int:pk>/load/', views.BookContentLoadView.as_view(), name='book_content_load'),
    path('api/book-content/<int:pk>/enhance/', views.BookContentEnhanceView.as_view(), name='book_content_enhance'),

    # User Resources — knowledge injection (PDF upload / URL)
    path('api/resources/<int:pk>/upload/', views.UploadResourceView.as_view(), name='upload_resource'),
    path('api/resources/<int:resource_pk>/delete/', views.DeleteResourceView.as_view(), name='delete_resource'),
]
