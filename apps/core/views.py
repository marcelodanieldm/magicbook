"""Views for MagicBook pages, AI generation endpoints and streaming workflows."""

import json
import re
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, DetailView, CreateView
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib import messages

from .models import Project, NicheAnalysis, OfferStructure, RevenueStrategy, ProductOutline, CopyLibrary, ChapterContent, UserResource, ProjectArtifact, TestRun, PlanAEnrollment, AvatarProfile
from .forms import ProjectCreateForm
from .services.ai_service import AIService

# Human-readable labels for the classic generation pipeline progress.
STEP_LABELS = ['Análisis de Nicho', 'Oferta Irresistible', 'Revenue', 'Índice E-book', 'Copies']

# Catalog for the complete Factory 16 workflow shown in the frontend.
FACTORY_15_FEATURES = [
    {'key': 'offer_modeling', 'name': 'Modelado de Oferta', 'owner': 'Backend + IA Engineer', 'source': 'native'},
    {'key': 'market_research', 'name': 'Investigación de Mercado', 'owner': 'Data Scientist + IA Engineer', 'source': 'native'},
    {'key': 'buyer_persona', 'name': 'Avatares & Buyer Persona', 'owner': 'Data Scientist + IA Engineer', 'source': 'native'},
    {'key': 'angles', 'name': 'Generador de Ángulos', 'owner': 'IA Engineer + Growth', 'source': 'artifact'},
    {'key': 'visual_identity', 'name': 'Identidad Visual', 'owner': 'Frontend + Brand Designer', 'source': 'artifact'},
    {'key': 'mockups', 'name': 'Mockups Premium', 'owner': 'IA Engineer + Designer', 'source': 'artifact'},
    {'key': 'ads_generator', 'name': 'Generador de Ads', 'owner': 'IA Engineer + Media Buyer', 'source': 'artifact'},
    {'key': 'landing_page', 'name': 'Landing Page', 'owner': 'Frontend + CRO', 'source': 'artifact'},
    {'key': 'product_copies', 'name': 'Copys de Producto', 'owner': 'Copywriter + IA Engineer', 'source': 'artifact'},
    {'key': 'ad_copies', 'name': 'Copys para Ads', 'owner': 'Copywriter + Media Buyer', 'source': 'artifact'},
    {'key': 'premium_scripts', 'name': 'Guiones Premium', 'owner': 'UGC Strategist + IA Engineer', 'source': 'artifact'},
    {'key': 'ugc_realistic', 'name': 'UGC Realistas', 'owner': 'UGC Strategist + IA Engineer', 'source': 'artifact'},
    {'key': 'product_generator', 'name': 'Generador de Producto', 'owner': 'Backend + IA Engineer', 'source': 'native'},
    {'key': 'upsell_aov', 'name': 'Upsells + AOV', 'owner': 'Revenue Manager + IA Engineer', 'source': 'native'},
    {'key': 'email_marketing', 'name': 'Email Marketing', 'owner': 'CRM + Copywriter', 'source': 'artifact'},
    {'key': 'global_export', 'name': 'Exportar y Vender Global', 'owner': 'Ops + Legal Strategy', 'source': 'artifact'},
]

# Benefits/features included in Plan A enrollment messaging.
PLAN_A_FEATURES = [
    {'key': 'simultaneous_tests', 'label': '+20 Testeos en simultáneo'},
    {'key': 'workflow_16_steps', 'label': 'Los 16 pasos del workflow completo'},
    {'key': 'unlimited_generation', 'label': 'Generación ilimitada por testeo'},
    {'key': 'market_research', 'label': 'Investigación de mercado profunda automatizada'},
    {'key': 'landing_page', 'label': 'Generador de Landing Page en 60 segundos'},
    {'key': 'premium_scripts', 'label': 'Generador de guiones y UGC que venden'},
    {'key': 'ad_copies', 'label': 'Generación de copys listos para usar'},
    {'key': 'nano_banana_ads', 'label': 'Generación de imágenes ADS con NANO BANANA 3 PRO'},
    {'key': 'product_bonus_pack', 'label': 'Generador de producto y bonus dentro de la app'},
    {'key': 'multi_market', 'label': 'Multi-mercado: AR, MX, CO, CL, UY, BR, ES + más'},
    {'key': 'offer_visual_model', 'label': 'Modelado de oferta con IA visual'},
    {'key': 'visual_identity', 'label': 'Logo + identidad visual con IA generativa'},
]


def _extract_base_price(offer) -> str:
    """Get a readable base price from offer fields for revenue prompt context."""
    if not offer:
        return '$27 USD'

    if offer.your_investment:
        return offer.your_investment

    for pp in offer.price_points or []:
        price = pp.get('price')
        if price:
            return f'${price} USD'

    return '$27 USD'


def _market_context(project) -> str:
    markets = project.target_markets or []
    if not markets:
        markets = [project.primary_market]
    return ', '.join(markets)


# ──────────────────────────────────────────────
# PUBLIC
# ──────────────────────────────────────────────

class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        features = [
            {'icon': '🎯', 'title': 'Analizador de Nicho', 'desc': 'Detecta los dolores profundos, deseos y miedos de tu avatar ideal con IA.'},
            {'icon': '💎', 'title': 'Oferta Irresistible', 'desc': 'Precio psicológico, bonuses con valor percibido y garantía que elimina el riesgo.'},
            {'icon': '📚', 'title': 'Índice del E-book', 'desc': '10 capítulos estructurados para máxima transformación y valor percibido.'},
            {'icon': '✍️', 'title': 'Copies de Venta', 'desc': 'Headlines, hooks para Ads y copies en formato PAS y AIDA listos para publicar.'},
        ]
        steps = [
            {'num': '1', 'title': 'Ingresa tu nicho o idea', 'desc': 'Escribe en lenguaje natural: "quiero vender un curso de cocina vegana para madres ocupadas."'},
            {'num': '2', 'title': 'La IA analiza el mercado', 'desc': 'MagicBook detecta el avatar, sus dolores profundos, deseos y las barreras de compra.'},
            {'num': '3', 'title': 'Construye tu oferta', 'desc': 'Genera el precio psicológico, bonuses irresistibles y la garantía perfecta.'},
            {'num': '4', 'title': 'Obtén tus copies listos', 'desc': 'Headlines, hooks para Meta y TikTok, y copies completos en PAS y AIDA.'},
        ]
        return render(request, 'home.html', {'features': features, 'steps': steps})


# ──────────────────────────────────────────────
# DASHBOARD (requires login)
# ──────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'core/dashboard.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).select_related(
            'niche_analysis', 'offer_structure', 'revenue_strategy', 'product_outline', 'copy_library'
        )


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectCreateForm
    template_name = 'core/project_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.target_markets = form.cleaned_data.get('target_markets', [])
        project = form.save()

        enrollment = getattr(self.request.user, 'plan_a_enrollment', None)
        if (enrollment and enrollment.status == 'active'
            and enrollment.first_project_launched_at is None):
            enrollment.first_project_launched_at = timezone.now()
            enrollment.save(update_fields=['first_project_launched_at', 'updated_at'])

        return redirect('core:project_detail', pk=project.pk)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'core/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        ctx['has_niche'] = hasattr(project, 'niche_analysis')
        ctx['has_offer'] = hasattr(project, 'offer_structure')
        ctx['has_revenue'] = hasattr(project, 'revenue_strategy')
        ctx['has_outline'] = hasattr(project, 'product_outline')
        ctx['has_copy'] = hasattr(project, 'copy_library')
        ctx['step_labels'] = STEP_LABELS
        ctx['step_labels_json'] = json.dumps(STEP_LABELS)
        # Build a dict {chapter_number: word_count} for written chapters
        written_chapters = {
            ch.chapter_number: ch.word_count
            for ch in project.chapter_contents.filter(status='done')
        }
        ctx['written_chapters'] = written_chapters
        ctx['written_count'] = len(written_chapters)
        return ctx


class ProjectFactoryView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'core/project_factory.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object

        artifacts = {
            a.artifact_type: a
            for a in project.artifacts.all()
        }

        features = []
        for f in FACTORY_15_FEATURES:
            status = 'pending'
            has_data = False

            if f['key'] == 'offer_modeling':
                has_data = hasattr(project, 'offer_structure')
            elif f['key'] == 'market_research':
                has_data = hasattr(project, 'niche_analysis')
            elif f['key'] == 'buyer_persona':
                has_data = hasattr(project, 'avatar_profile') and bool(project.avatar_profile.avatars)
            elif f['key'] == 'product_generator':
                has_data = hasattr(project, 'product_outline')
            elif f['key'] == 'upsell_aov':
                has_data = hasattr(project, 'revenue_strategy')
            else:
                art = artifacts.get(f['key'])
                has_data = bool(art and art.status == 'done')

            if has_data:
                status = 'done'

            features.append({
                **f,
                'status': status,
                'artifact': artifacts.get(f['key']),
            })

        done = sum(1 for f in features if f['status'] == 'done')
        running_tests = TestRun.objects.filter(
            project__user=self.request.user,
            status='running',
        ).count()

        feature_done = {f['key']: (f['status'] == 'done') for f in features}
        plan_a_status = [
            {
                **item,
                'done': (
                    running_tests <= project.max_simultaneous_tests
                    if item['key'] == 'simultaneous_tests'
                    else (len(FACTORY_15_FEATURES) >= 16 if item['key'] == 'workflow_16_steps'
                          else (project.plan_tier == 'plan_a_29' if item['key'] == 'unlimited_generation'
                                else (len(project.target_markets or []) > 1 if item['key'] == 'multi_market'
                                      else feature_done.get(item['key'], False))))
                )
            }
            for item in PLAN_A_FEATURES
        ]

        ctx['features'] = features
        ctx['done_count'] = done
        ctx['total_count'] = len(features)
        ctx['running_tests_count'] = running_tests
        ctx['max_simultaneous_tests'] = project.max_simultaneous_tests
        ctx['plan_a_features'] = plan_a_status
        ctx['target_markets_label'] = _market_context(project)
        ctx['last_test_run'] = project.test_runs.first()
        ctx['avatar_profile'] = getattr(project, 'avatar_profile', None)
        ctx['niche_analysis'] = getattr(project, 'niche_analysis', None)
        ctx['offer_structure'] = getattr(project, 'offer_structure', None)
        ctx['revenue_strategy'] = getattr(project, 'revenue_strategy', None)
        return ctx


# ──────────────────────────────────────────────
# AI GENERATION ENDPOINTS
# ──────────────────────────────────────────────

class GenerateNicheView(LoginRequiredMixin, View):
    """POST /api/generate/niche/<pk>/ → runs niche analysis and saves result."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            service = AIService(brand_voice=project.brand_voice)
            data = service.analyze_niche(project.niche_input)

            NicheAnalysis.objects.update_or_create(
                project=project,
                defaults={
                    'avatar_name': data.get('avatar_name', ''),
                    'buyer_personas': data.get('buyer_personas', []),
                    'pains': data.get('pains', []),
                    'desires': data.get('desires', []),
                    'fears': data.get('fears', []),
                    'barriers': data.get('barriers', []),
                    'product_names': data.get('product_names', []),
                    'epiphany_bridge': data.get('epiphany_bridge', ''),
                    'raw_response': data.get('raw_response', ''),
                },
            )

            # Auto-set title from first product name suggestion
            if not project.title and data.get('product_names'):
                project.title = data['product_names'][0]

            project.status = 'niche_done'
            project.save()

            return JsonResponse({'success': True, 'progress': 25})

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class GenerateFactoryArtifactView(LoginRequiredMixin, View):
    """POST /api/generate/factory/<pk>/<artifact_type>/"""

    def post(self, request, pk, artifact_type):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        allowed = {f['key'] for f in FACTORY_15_FEATURES if f['source'] == 'artifact'}
        if artifact_type not in allowed:
            return JsonResponse({'success': False, 'error': 'Tipo de artefacto no permitido.'}, status=400)

        try:
            service = AIService(
                model=project.ai_model,
                brand_voice=project.brand_voice,
            )
            data = service.generate_factory_artifact(project, artifact_type)

            art, _ = ProjectArtifact.objects.update_or_create(
                project=project,
                artifact_type=artifact_type,
                defaults={
                    'title': next((f['name'] for f in FACTORY_15_FEATURES if f['key'] == artifact_type), artifact_type),
                    'payload': {k: v for k, v in data.items() if k != 'raw_response'},
                    'raw_response': data.get('raw_response', ''),
                    'status': 'done',
                }
            )

            return JsonResponse({
                'success': True,
                'artifact_type': artifact_type,
                'title': art.title,
                'payload': art.payload,
            })
        except Exception as exc:
            ProjectArtifact.objects.update_or_create(
                project=project,
                artifact_type=artifact_type,
                defaults={
                    'title': artifact_type,
                    'payload': {},
                    'raw_response': '',
                    'status': 'error',
                }
            )
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class ArtifactDetailView(LoginRequiredMixin, View):
    """GET /api/artifact/<pk>/<artifact_type>/detail/ → returns rendered payload JSON."""

    def get(self, request, pk, artifact_type):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        art = ProjectArtifact.objects.filter(project=project, artifact_type=artifact_type).first()
        if not art or art.status != 'done':
            return JsonResponse({'success': False, 'error': 'Artefacto no generado todavía.'}, status=404)
        return JsonResponse({'success': True, 'payload': art.payload, 'title': art.title})


class StartPlanATestRunView(LoginRequiredMixin, View):
    """POST /api/plan-a/test-run/<pk>/start/"""

    DEFAULT_FEATURES = [
        'angles',
        'visual_identity',
        'offer_visual_model',
        'mockups',
        'ads_generator',
        'nano_banana_ads',
        'landing_page',
        'product_copies',
        'ad_copies',
        'premium_scripts',
        'ugc_realistic',
        'product_bonus_pack',
        'email_marketing',
        'global_export',
    ]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        running = TestRun.objects.filter(
            project__user=request.user,
            status='running',
        ).count()
        if running >= project.max_simultaneous_tests:
            return JsonResponse(
                {
                    'success': False,
                    'error': f'Límite alcanzado: {project.max_simultaneous_tests} testeos simultáneos.'
                },
                status=429,
            )

        run = TestRun.objects.create(
            project=project,
            status='running',
            requested_features=self.DEFAULT_FEATURES,
        )

        generated = 0
        try:
            service = AIService(model=project.ai_model, brand_voice=project.brand_voice)

            for artifact_type in self.DEFAULT_FEATURES:
                data = service.generate_factory_artifact(project, artifact_type)
                ProjectArtifact.objects.update_or_create(
                    project=project,
                    artifact_type=artifact_type,
                    defaults={
                        'title': artifact_type,
                        'payload': {k: v for k, v in data.items() if k != 'raw_response'},
                        'raw_response': data.get('raw_response', ''),
                        'status': 'done',
                    },
                )
                generated += 1

            run.status = 'completed'
            run.generated_count = generated
            run.finished_at = timezone.now()
            run.save(update_fields=['status', 'generated_count', 'finished_at'])
            return JsonResponse({'success': True, 'generated_count': generated, 'run_id': run.pk})

        except Exception as exc:
            run.status = 'failed'
            run.generated_count = generated
            run.error_message = str(exc)
            run.finished_at = timezone.now()
            run.save(update_fields=['status', 'generated_count', 'error_message', 'finished_at'])
            return JsonResponse({'success': False, 'error': str(exc), 'generated_count': generated}, status=500)


class GenerateOfferView(LoginRequiredMixin, View):
    """POST /api/generate/offer/<pk>/ → generates offer structure."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        if not hasattr(project, 'niche_analysis'):
            return JsonResponse(
                {'success': False, 'error': 'Primero genera el análisis de nicho.'}, status=400
            )

        try:
            service = AIService(brand_voice=project.brand_voice)
            niche = project.niche_analysis
            niche_data = {
                'avatar_name': niche.avatar_name,
                'pains': niche.pains,
                'desires': niche.desires,
            }
            data = service.generate_offer(project.niche_input, niche_data)

            OfferStructure.objects.update_or_create(
                project=project,
                defaults={
                    'product_name': data.get('product_name', ''),
                    'tagline': data.get('tagline', ''),
                    'price_points': data.get('price_points', []),
                    'bonuses': data.get('bonuses', []),
                    'guarantee': data.get('guarantee', ''),
                    'value_stack': data.get('value_stack', []),
                    'total_value': data.get('total_value', ''),
                    'your_investment': data.get('your_investment', ''),
                    'upsell': data.get('upsell', {}),
                    'order_bump': data.get('order_bump', {}),
                    'raw_response': data.get('raw_response', ''),
                },
            )

            project.status = 'offer_done'
            project.save()

            return JsonResponse({'success': True, 'progress': 50})

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class GenerateAvatarsView(LoginRequiredMixin, View):
    """POST /api/generate/avatars/<pk>/ → generates buyer personas for the project."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            service = AIService(brand_voice=project.brand_voice)
            data = service.generate_avatars(project)

            AvatarProfile.objects.update_or_create(
                project=project,
                defaults={
                    'avatars': data.get('avatars', []),
                    'buyer_persona_summary': data.get('buyer_persona_summary', ''),
                    'raw_response': data.get('raw_response', ''),
                },
            )
            return JsonResponse({
                'success': True,
                'avatars': data.get('avatars', []),
                'summary': data.get('buyer_persona_summary', ''),
            })
        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class GenerateRevenueView(LoginRequiredMixin, View):
    """POST /api/generate/revenue/<pk>/ → generates order bump + upsell strategy."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        if not hasattr(project, 'offer_structure'):
            return JsonResponse(
                {'success': False, 'error': 'Primero genera la estructura de oferta.'}, status=400
            )

        try:
            service = AIService(brand_voice=project.brand_voice)

            offer = project.offer_structure
            niche = getattr(project, 'niche_analysis', None)

            product_title = offer.product_name or project.title or project.niche_input
            base_price = _extract_base_price(offer)
            avatar_pain = ''
            if niche and niche.pains:
                avatar_pain = niche.pains[0]
            if not avatar_pain:
                avatar_pain = project.niche_input

            data = service.generate_revenue_strategy(
                product_title=product_title,
                base_price=base_price,
                avatar_pain=avatar_pain,
            )

            RevenueStrategy.objects.update_or_create(
                project=project,
                defaults={
                    'order_bump': data.get('order_bump', {}),
                    'upsell': data.get('upsell', {}),
                    'raw_response': data.get('raw_response', ''),
                },
            )

            project.status = 'revenue_done'
            project.save(update_fields=['status'])

            return JsonResponse({'success': True, 'progress': 60})

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class GenerateOutlineView(LoginRequiredMixin, View):
    """POST /api/generate/outline/<pk>/ → generates product outline."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        if not hasattr(project, 'offer_structure'):
            return JsonResponse(
                {'success': False, 'error': 'Primero genera la estructura de oferta.'}, status=400
            )

        try:
            service = AIService(brand_voice=project.brand_voice)
            offer = project.offer_structure
            offer_data = {
                'product_name': offer.product_name,
                'tagline': offer.tagline,
            }
            data = service.generate_outline(project.niche_input, offer_data)

            ProductOutline.objects.update_or_create(
                project=project,
                defaults={
                    'product_type': data.get('product_type', 'ebook'),
                    'title': data.get('title', ''),
                    'subtitle': data.get('subtitle', ''),
                    'description': data.get('description', ''),
                    'chapters': data.get('chapters', []),
                    'raw_response': data.get('raw_response', ''),
                },
            )

            project.status = 'outline_done'
            project.save()

            return JsonResponse({'success': True, 'progress': 75})

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class GenerateCopyView(LoginRequiredMixin, View):
    """POST /api/generate/copy/<pk>/ → generates copy library."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        if not hasattr(project, 'product_outline'):
            return JsonResponse(
                {'success': False, 'error': 'Primero genera el índice del producto.'}, status=400
            )

        try:
            service = AIService(brand_voice=project.brand_voice)
            offer = project.offer_structure
            niche = project.niche_analysis
            offer_data = {'product_name': offer.product_name, 'tagline': offer.tagline}
            niche_data = {'pains': niche.pains}

            data = service.generate_copy(project.niche_input, offer_data, niche_data)

            CopyLibrary.objects.update_or_create(
                project=project,
                defaults={
                    'headlines': data.get('headlines', []),
                    'hooks': data.get('hooks', []),
                    'short_description': data.get('short_description', ''),
                    'pas_copy': data.get('pas_copy', ''),
                    'aida_copy': data.get('aida_copy', ''),
                    'cta_options': data.get('cta_options', []),
                    'raw_response': data.get('raw_response', ''),
                },
            )

            project.status = 'copy_done'
            project.save()

            return JsonResponse({'success': True, 'progress': 100})

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class GenerateAllView(LoginRequiredMixin, View):
    """
    POST /api/generate/all/<pk>/
    Runs the unified strategic generation flow and saves all modules:
    niche, offer, outline, copy and revenue strategy.
    """

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            service = AIService(
                model=project.ai_model,
                brand_voice=project.brand_voice,
            )
            result = service.generate_all(project.niche_input)

            # ── Niche Analysis ──────────────────────────────
            na = result.get('niche_analysis', {})
            NicheAnalysis.objects.update_or_create(
                project=project,
                defaults={
                    'avatar_name': na.get('avatar_name', ''),
                    'buyer_personas': na.get('buyer_personas', []),
                    'pains': na.get('pains', []),
                    'desires': na.get('desires', []),
                    'fears': na.get('fears', []),
                    'barriers': na.get('barriers', []),
                    'product_names': na.get('product_names', []),
                    'epiphany_bridge': na.get('epiphany_bridge', ''),
                    'raw_response': result.get('raw_response', ''),
                },
            )

            # ── Offer Structure ─────────────────────────────
            os_data = result.get('offer_structure', {})
            OfferStructure.objects.update_or_create(
                project=project,
                defaults={
                    'product_name': os_data.get('product_name', ''),
                    'tagline': os_data.get('tagline', ''),
                    'price_points': os_data.get('price_points', []),
                    'bonuses': os_data.get('bonuses', []),
                    'guarantee': os_data.get('guarantee', ''),
                    'value_stack': os_data.get('value_stack', []),
                    'total_value': os_data.get('total_value', ''),
                    'your_investment': os_data.get('your_investment', ''),
                    'upsell': os_data.get('upsell', {}),
                    'order_bump': os_data.get('order_bump', {}),
                    'raw_response': result.get('raw_response', ''),
                },
            )

            # ── Product Outline ─────────────────────────────
            po = result.get('product_outline', {})
            ProductOutline.objects.update_or_create(
                project=project,
                defaults={
                    'product_type': po.get('product_type', 'ebook'),
                    'title': po.get('title', ''),
                    'subtitle': po.get('subtitle', ''),
                    'description': po.get('description', ''),
                    'chapters': po.get('chapters', []),
                    'raw_response': result.get('raw_response', ''),
                },
            )

            # ── Copy Library ────────────────────────────────
            cl = result.get('copy_library', {})
            # Merge ad_angles into hooks list for unified display
            hooks = cl.get('hooks', [])
            ad_angles = cl.get('ad_angles', [])
            if ad_angles:
                for angle in ad_angles:
                    hooks.insert(0, {
                        'type': f"Ángulo: {angle.get('angle', '')}",
                        'platform': 'Meta Ads (Facebook/Instagram)',
                        'text': angle.get('hook', ''),
                    })

            CopyLibrary.objects.update_or_create(
                project=project,
                defaults={
                    'headlines': cl.get('headlines', []),
                    'hooks': hooks,
                    'short_description': cl.get('short_description', ''),
                    'pas_copy': cl.get('pas_copy', ''),
                    'aida_copy': cl.get('aida_copy', ''),
                    'cta_options': cl.get('cta_options', []),
                    'raw_response': result.get('raw_response', ''),
                },
            )

            # ── Revenue Strategy (extra specialized call) ───
            revenue = service.generate_revenue_strategy(
                product_title=os_data.get('product_name') or project.title or project.niche_input,
                base_price=os_data.get('your_investment') or '$27 USD',
                avatar_pain=(na.get('pains', ['']) or [''])[0] or project.niche_input,
            )
            RevenueStrategy.objects.update_or_create(
                project=project,
                defaults={
                    'order_bump': revenue.get('order_bump', {}),
                    'upsell': revenue.get('upsell', {}),
                    'raw_response': revenue.get('raw_response', ''),
                },
            )

            # ── Update project ──────────────────────────────
            if not project.title and os_data.get('product_name'):
                project.title = os_data['product_name']
            project.status = 'copy_done'
            project.save()

            return JsonResponse({'success': True, 'progress': 100, 'mode': 'full'})

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


# ──────────────────────────────────────────────
# DELETE PROJECT
# ──────────────────────────────────────────────

class ProjectDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        project.delete()
        messages.success(request, 'Proyecto eliminado correctamente.')
        return redirect('core:dashboard')


# ──────────────────────────────────────────────
# CHAPTER WRITER (Phase 2 Chaining)
# ──────────────────────────────────────────────

class WriteChapterView(LoginRequiredMixin, View):
    """
    POST /api/write/chapter/<pk>/<int:chapter_num>/
    Writes a single chapter using the Chapter Writer AI prompt.
    Saves result to ChapterContent and returns JSON.
    """

    def post(self, request, pk, chapter_num):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        if not hasattr(project, 'product_outline'):
            return JsonResponse(
                {'success': False, 'error': 'Primero genera el índice del producto.'},
                status=400,
            )

        chapters = project.product_outline.chapters or []
        # chapter_num is 1-based
        if chapter_num < 1 or chapter_num > len(chapters):
            return JsonResponse(
                {'success': False, 'error': f'Capítulo {chapter_num} no existe en el índice.'},
                status=400,
            )

        chapter_data = chapters[chapter_num - 1]
        # Ensure the dict carries the chapter number
        chapter_data['number'] = chapter_num

        # Load previously written chapters for continuity context
        previous_chapters = list(
            ChapterContent.objects.filter(
                project=project,
                status='done',
            ).exclude(chapter_number=chapter_num).order_by('chapter_number')
        )

        try:
            service = AIService(
                model=project.ai_model,
                brand_voice=project.brand_voice,
            )
            content = service.write_chapter(project, chapter_data, previous_chapters)

            word_count = len(content.split())

            ChapterContent.objects.update_or_create(
                project=project,
                chapter_number=chapter_num,
                defaults={
                    'title': chapter_data.get('title', f'Capítulo {chapter_num}'),
                    'content': content,
                    'word_count': word_count,
                    'status': 'done',
                },
            )

            return JsonResponse({
                'success': True,
                'chapter_number': chapter_num,
                'title': chapter_data.get('title', ''),
                'word_count': word_count,
                'content': content,
            })

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)



# ──────────────────────────────────────────────────────────────────
# WRITE ALL CHAPTERS — Fábrica (SSE stream)
# ──────────────────────────────────────────────────────────────────

class WriteAllChaptersView(LoginRequiredMixin, View):
    """
    GET /api/write/all-chapters/<pk>/
    Streams Server-Sent Events while writing each chapter sequentially.
    EventSource connects; each chapter done → SSE event; final 'complete' event
    carries total word count so the client can show a download button.
    """

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)

        if not hasattr(project, 'product_outline'):
            def error_stream():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Primero genera el índice del producto.'})}\n\n"
            resp = StreamingHttpResponse(error_stream(), content_type='text/event-stream')
            resp['Cache-Control'] = 'no-cache'
            return resp

        def event_stream(project_pk):
            # Re-fetch inside generator to avoid stale / closed DB connections
            from .models import Project as _P, ChapterContent as _CC, UserResource as _UR
            _project = _P.objects.get(pk=project_pk)
            chapters  = _project.product_outline.chapters or []
            total     = len(chapters)

            # Build combined user-knowledge context from all resources
            resources    = _UR.objects.filter(project=_project).exclude(extracted_text='')
            user_context = '\n\n---\n\n'.join(
                f"[{r.resource_type.upper()}] {r.title or r.url}:\n{r.extracted_text}"
                for r in resources
            )

            service = AIService(model=_project.ai_model, brand_voice=_project.brand_voice)

            for i, ch_data in enumerate(chapters, 1):
                ch_data = dict(ch_data)   # don't mutate stored JSON
                ch_data['number'] = i

                previous = list(
                    _CC.objects.filter(project=_project, status='done')
                               .order_by('chapter_number')
                )

                try:
                    content    = service.write_chapter(_project, ch_data, previous,
                                                       user_context=user_context)
                    word_count = len(content.split())

                    _CC.objects.update_or_create(
                        project=_project,
                        chapter_number=i,
                        defaults={
                            'title':      ch_data.get('title', f'Capítulo {i}'),
                            'content':    content,
                            'word_count': word_count,
                            'status':     'done',
                        },
                    )
                    yield f"data: {json.dumps({'type': 'chapter_done', 'chapter': i, 'total': total, 'title': ch_data.get('title', ''), 'word_count': word_count})}\n\n"

                except Exception as exc:
                    yield f"data: {json.dumps({'type': 'chapter_error', 'chapter': i, 'error': str(exc)})}\n\n"

            # All chapters done — mark project complete and emit final event
            total_words = sum(
                ch.word_count for ch in _CC.objects.filter(project=_project, status='done')
            )
            _project.status = 'complete'
            _project.save(update_fields=['status'])

            yield f"data: {json.dumps({'type': 'complete', 'total_words': total_words, 'chapters_written': _CC.objects.filter(project=_project, status='done').count()})}\n\n"

        response = StreamingHttpResponse(event_stream(project.pk), content_type='text/event-stream')
        response['Cache-Control']      = 'no-cache'
        response['X-Accel-Buffering']  = 'no'
        return response


# ──────────────────────────────────────────────────────────────────
# DOWNLOAD E-BOOK — assembles all chapters into a .md file
# ──────────────────────────────────────────────────────────────────

class DownloadEbookView(LoginRequiredMixin, View):
    """
    GET /api/download/ebook/<pk>/
    Assembles written ChapterContent records with intro + conclusion and
    serves a Markdown file as an attachment.
    """

    def get(self, request, pk):
        project  = get_object_or_404(Project, pk=pk, user=request.user)
        chapters = ChapterContent.objects.filter(
            project=project, status='done'
        ).order_by('chapter_number')

        if not chapters.exists():
            return HttpResponse('No hay capítulos escritos todavía.', status=400)

        book_title = project.title or project.niche_input
        avatar = getattr(getattr(project, 'niche_analysis', None), 'avatar_name', '')

        lines = []
        lines.append(f'# {book_title}\n')

        tagline = getattr(getattr(project, 'offer_structure', None), 'tagline', '')
        if tagline:
            lines.append(f'_{tagline}_\n')

        lines.append('---\n')

        # Auto-generated introduction
        lines.append('## Introducción\n')
        if avatar:
            lines.append(
                f'Este libro ha sido creado especialmente para **{avatar}**. '
                'A lo largo de sus capítulos descubrirás metodologías, estrategias y '
                'ejercicios prácticos que transformarán tu perspectiva y tus resultados. '
                'Lee con lápiz en mano: subraya, anota y, sobre todo, **actúa** — '
                'es el único camino.\n'
            )
        else:
            lines.append(
                'Bienvenido/a. Este libro es tu hoja de ruta hacia la transformación '
                'que buscas. Cada capítulo está diseñado para llevarte paso a paso '
                'desde donde estás hasta donde quieres estar.\n'
            )

        lines.append('---\n')

        total_words = 0
        for ch in chapters:
            lines.append(f'## Capítulo {ch.chapter_number}: {ch.title}\n')
            lines.append(ch.content)
            lines.append('\n---\n')
            total_words += ch.word_count

        # Auto-generated conclusion
        lines.append('## Conclusión: Tu Próximo Paso\n')
        lines.append(
            'Has completado este libro. El conocimiento que acabas de adquirir es '
            'poderoso, pero solo tiene valor si lo pones en práctica.\n\n'
            '**Tu única tarea ahora mismo:** elige UN concepto de este libro y aplica '
            'una acción concreta antes de que termine el día. Una acción. Hoy.\n'
        )

        lines.append('---\n')
        lines.append(
            f'_Generado con MagicBook · {total_words:,} palabras · '
            f'{chapters.count()} capítulos_\n'
        )

        markdown_content = '\n'.join(lines)

        safe_title = re.sub(r'[^\w\s-]', '', book_title)[:50].strip()
        safe_title = re.sub(r'\s+', '_', safe_title)
        filename   = f'{safe_title}_ebook.md'

        response = HttpResponse(markdown_content, content_type='text/markdown; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ──────────────────────────────────────────────────────────────────
# USER RESOURCES — upload PDF / URL for knowledge injection
# ──────────────────────────────────────────────────────────────────

class UploadResourceView(LoginRequiredMixin, View):
    """
    POST /api/resources/<pk>/upload/
    Accepts a PDF file OR a URL, extracts text, saves as UserResource.
    """

    def post(self, request, pk):
        from .services.resource_extractor import extract_from_pdf, extract_from_url

        project       = get_object_or_404(Project, pk=pk, user=request.user)
        resource_type = request.POST.get('resource_type', '').strip()

        if resource_type not in ('pdf', 'url'):
            return JsonResponse(
                {'success': False, 'error': 'resource_type debe ser "pdf" o "url"'}, status=400
            )

        try:
            if resource_type == 'url':
                url = request.POST.get('url', '').strip()
                if not url:
                    return JsonResponse({'success': False, 'error': 'Se requiere una URL.'}, status=400)

                title     = request.POST.get('title', '').strip() or url[:100]
                extracted = extract_from_url(url)
                resource  = UserResource.objects.create(
                    project=project, resource_type='url',
                    title=title, url=url,
                    extracted_text=extracted, char_count=len(extracted),
                )

            else:  # pdf
                pdf_file = request.FILES.get('pdf_file')
                if not pdf_file:
                    return JsonResponse({'success': False, 'error': 'No se recibió ningún archivo PDF.'}, status=400)
                if not pdf_file.name.lower().endswith('.pdf'):
                    return JsonResponse({'success': False, 'error': 'Solo se aceptan archivos .pdf'}, status=400)
                if pdf_file.size > 20 * 1024 * 1024:
                    return JsonResponse({'success': False, 'error': 'El archivo no debe superar 20 MB.'}, status=400)

                title    = request.POST.get('title', '').strip() or pdf_file.name
                resource = UserResource.objects.create(
                    project=project, resource_type='pdf',
                    title=title, pdf_file=pdf_file,
                )
                # Extract after file is on disk
                extracted = extract_from_pdf(resource.pdf_file.path)
                resource.extracted_text = extracted
                resource.char_count     = len(extracted)
                resource.save(update_fields=['extracted_text', 'char_count'])

            return JsonResponse({
                'success':       True,
                'id':            resource.pk,
                'title':         resource.title,
                'resource_type': resource.resource_type,
                'char_count':    resource.char_count,
            })

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class DeleteResourceView(LoginRequiredMixin, View):
    """
    POST /api/resources/<int:resource_pk>/delete/
    Deletes a UserResource owned by the current user's project.
    """

    def post(self, request, resource_pk):
        resource = get_object_or_404(
            UserResource, pk=resource_pk, project__user=request.user
        )
        resource.delete()
        return JsonResponse({'success': True})
