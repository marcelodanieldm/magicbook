"""Views for MagicBook pages, AI generation endpoints and streaming workflows."""

import json
import re
from django.utils import timezone
from django.utils.translation import get_language
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, DetailView, CreateView
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib import messages

from .models import Project, NicheAnalysis, OfferStructure, RevenueStrategy, ProductOutline, CopyLibrary, ChapterContent, UserResource, ProjectArtifact, TestRun, PlanAEnrollment, AvatarProfile, ChapterRewriteHistory, WorkflowProject, ProjectStep, BookChapter, BookContent
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

DASHBOARD_PHASES = [
    {
        'title': 'Fase 1: Estrategia (ADN)',
        'modules': [
            {'icon': '🎯', 'name': 'Modelado de Oferta', 'desc': 'Define nicho, país y precio para obtener la Gran Promesa.'},
            {'icon': '🔍', 'name': 'Investigación', 'desc': 'Detecta tendencias, competencia y oportunidades ignoradas.'},
            {'icon': '👥', 'name': 'Avatares', 'desc': 'Genera 3 perfiles de cliente con miedos y deseos profundos.'},
            {'icon': '⚔️', 'name': 'Ángulos de Venta', 'desc': 'Propone 5 enfoques de venta listos para testear.'},
        ],
    },
    {
        'title': 'Fase 2: Visual & Branding',
        'modules': [
            {'icon': '🎨', 'name': 'Identidad Visual', 'desc': 'Paleta HEX, tipografías y concepto de logo.'},
            {'icon': '🖼️', 'name': 'Mockups Premium', 'desc': 'Visuales del producto en móvil, tablet o impreso.'},
            {'icon': '📢', 'name': 'Generador de Ads', 'desc': 'Creativos publicitarios basados en ángulos de venta.'},
        ],
    },
    {
        'title': 'Fase 3: Embudo de Ventas',
        'modules': [
            {'icon': '🚀', 'name': 'Landing Page', 'desc': 'Genera y edita página de venta con preview.'},
            {'icon': '✍️', 'name': 'Copys de Producto', 'desc': 'Textos persuasivos para checkout y página de pago.'},
            {'icon': '🎬', 'name': 'Guiones de Video', 'desc': 'Scripts para VSL o reels de conversión.'},
            {'icon': '📱', 'name': 'Prompts UGC', 'desc': 'Instrucciones para anuncios estilo creador.'},
        ],
    },
    {
        'title': 'Fase 4: The Factory',
        'modules': [
            {'icon': '📦', 'name': 'Infoproducto', 'desc': 'Redacción masiva de capítulos del e-book.'},
            {'icon': '💰', 'name': 'Upsells + AOV', 'desc': 'Oferta complementaria para subir ticket.'},
            {'icon': '📧', 'name': 'Email Marketing', 'desc': 'Secuencia de 7 correos para conversión.'},
        ],
    },
    {
        'title': 'Fase 5: Operaciones (Scale)',
        'modules': [
            {'icon': '🌎', 'name': 'Exportación', 'desc': 'Guía para ventas globales y operación internacional.'},
            {'icon': '🏆', 'name': 'Campus VIP', 'desc': 'Comunidad y clases para escalar resultados.'},
        ],
    },
]

WORKFLOW_STEP_BLUEPRINT = [
    (1, 'Modelado de Oferta'),
    (2, 'Investigación'),
    (3, 'Avatares'),
    (4, 'Ángulos de Venta'),
    (5, 'Identidad Visual'),
    (6, 'Mockups Premium'),
    (7, 'Generador de Ads'),
    (8, 'Landing Page'),
    (9, 'Copys de Producto'),
    (10, 'Guiones de Video'),
    (11, 'Prompts UGC'),
    (12, 'Infoproducto'),
    (13, 'Upsells + AOV'),
    (14, 'Email Marketing'),
    (15, 'Exportación'),
    (16, 'Campus VIP'),
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


def _first_text(value):
    """Extract the first readable string from nested payload-like structures."""
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list):
        for item in value:
            text = _first_text(item)
            if text:
                return text
    if isinstance(value, dict):
        for key in ('title', 'name', 'tagline', 'summary', 'hook', 'description', 'text', 'headline'):
            text = _first_text(value.get(key))
            if text:
                return text
        for item in value.values():
            text = _first_text(item)
            if text:
                return text
    return ''


def _find_first_image_url(value):
    """Find first URL-like image from nested payload structures."""
    if isinstance(value, str):
        low = value.lower()
        if low.startswith('http') and any(ext in low for ext in ('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            return value
        return ''
    if isinstance(value, list):
        for item in value:
            found = _find_first_image_url(item)
            if found:
                return found
    if isinstance(value, dict):
        for key in ('thumbnail', 'thumbnail_url', 'image', 'image_url', 'preview', 'preview_url', 'mockup_url', 'url'):
            found = _find_first_image_url(value.get(key))
            if found:
                return found
        for item in value.values():
            found = _find_first_image_url(item)
            if found:
                return found
    return ''


def _artifact_payload(project, artifact_type):
    art = project.artifacts.filter(artifact_type=artifact_type, status='done').first()
    return art.payload if art else None


def _ensure_workflow_project(project):
    workflow_project, created = WorkflowProject.objects.get_or_create(
        source_project=project,
        defaults={
            'user': project.user,
            'title': project.title or project.niche_input[:90],
            'niche': project.niche_input,
            'target_country': project.primary_market,
            'target_audience': '',
            'status': 'active' if project.status != 'complete' else 'completed',
            'progress_percentage': 0,
        },
    )
    if not created:
        changed = False
        new_title = project.title or project.niche_input[:90]
        if workflow_project.title != new_title:
            workflow_project.title = new_title
            changed = True
        if workflow_project.niche != project.niche_input:
            workflow_project.niche = project.niche_input
            changed = True
        if workflow_project.target_country != project.primary_market:
            workflow_project.target_country = project.primary_market
            changed = True
        expected_status = 'completed' if project.status == 'complete' else 'active'
        if workflow_project.status != expected_status:
            workflow_project.status = expected_status
            changed = True
        if changed:
            workflow_project.save(update_fields=['title', 'niche', 'target_country', 'status'])
    return workflow_project


def _step_content_snapshot(project, step_number):
    niche = getattr(project, 'niche_analysis', None)
    offer = getattr(project, 'offer_structure', None)
    avatars = getattr(project, 'avatar_profile', None)
    revenue = getattr(project, 'revenue_strategy', None)
    outline = getattr(project, 'product_outline', None)
    copy_lib = getattr(project, 'copy_library', None)

    if step_number == 1 and offer:
        return True, {
            'product_name': offer.product_name,
            'tagline': offer.tagline,
            'price_points': offer.price_points,
            'guarantee': offer.guarantee,
        }
    if step_number == 2 and niche:
        return True, {
            'avatar_name': niche.avatar_name,
            'pains': niche.pains,
            'desires': niche.desires,
        }
    if step_number == 3 and avatars and avatars.avatars:
        return True, {'avatars': avatars.avatars, 'summary': avatars.buyer_persona_summary}
    if step_number == 4:
        payload = _artifact_payload(project, 'angles')
        return (bool(payload), payload)
    if step_number == 5:
        payload = _artifact_payload(project, 'visual_identity')
        return (bool(payload), payload)
    if step_number == 6:
        payload = _artifact_payload(project, 'mockups')
        return (bool(payload), payload)
    if step_number == 7:
        payload = _artifact_payload(project, 'ads_generator')
        return (bool(payload), payload)
    if step_number == 8:
        payload = _artifact_payload(project, 'landing_page')
        return (bool(payload), payload)
    if step_number == 9 and copy_lib:
        return True, {
            'headlines': copy_lib.headlines,
            'hooks': copy_lib.hooks,
            'cta_options': copy_lib.cta_options,
        }
    if step_number == 10:
        payload = _artifact_payload(project, 'premium_scripts')
        return (bool(payload), payload)
    if step_number == 11:
        payload = _artifact_payload(project, 'ugc_realistic')
        return (bool(payload), payload)
    if step_number == 12:
        chapters = list(project.chapter_contents.filter(status='done').values(
            'chapter_number', 'title', 'word_count', 'updated_at'
        ))
        if chapters:
            return True, {'chapters': chapters, 'count': len(chapters)}
        if outline:
            return True, {'outline': outline.chapters}
    if step_number == 13 and revenue:
        return True, {'order_bump': revenue.order_bump, 'upsell': revenue.upsell}
    if step_number == 14:
        payload = _artifact_payload(project, 'email_marketing')
        return (bool(payload), payload)
    if step_number == 15:
        payload = _artifact_payload(project, 'global_export')
        return (bool(payload), payload)
    if step_number == 16:
        enrollment = getattr(project.user, 'plan_a_enrollment', None)
        plan_b = getattr(project.user, 'plan_b_enrollment', None)
        active = bool((enrollment and enrollment.status == 'active') or (plan_b and plan_b.status == 'active'))
        return (active, {'membership': 'active' if active else 'pending'})
    return False, None


def _sync_workflow_from_project(project):
    workflow_project = _ensure_workflow_project(project)

    completed_count = 0
    for step_number, step_name in WORKFLOW_STEP_BLUEPRINT:
        is_completed, content = _step_content_snapshot(project, step_number)
        if is_completed:
            completed_count += 1
        ProjectStep.objects.update_or_create(
            project=workflow_project,
            step_number=step_number,
            defaults={
                'step_name': step_name,
                'content': content,
                'is_completed': is_completed,
            },
        )

    chapters = list(project.chapter_contents.all())
    current_numbers = set()
    for chapter in chapters:
        current_numbers.add(chapter.chapter_number)
        BookChapter.objects.update_or_create(
            project=workflow_project,
            chapter_number=chapter.chapter_number,
            defaults={
                'title': chapter.title,
                'body_text': chapter.content,
                'status': 'done' if chapter.status == 'done' else 'draft',
            },
        )

    if current_numbers:
        BookChapter.objects.filter(project=workflow_project).exclude(chapter_number__in=current_numbers).delete()

    progress = int((completed_count / 16) * 100)
    workflow_status = 'completed' if completed_count >= 16 else 'active'
    if workflow_project.progress_percentage != progress or workflow_project.status != workflow_status:
        workflow_project.progress_percentage = progress
        workflow_project.status = workflow_status
        workflow_project.save(update_fields=['progress_percentage', 'status'])

    return workflow_project


def _build_launch_map_nodes(project):
    """Builds the 16-step launch map status and quick summaries for dashboard popovers."""
    artifacts = {a.artifact_type: a for a in project.artifacts.all()}

    offer = getattr(project, 'offer_structure', None)
    niche = getattr(project, 'niche_analysis', None)
    avatars = getattr(project, 'avatar_profile', None)
    revenue = getattr(project, 'revenue_strategy', None)
    outline = getattr(project, 'product_outline', None)

    specs = [
        ('offer_modeling', 'Oferta', bool(offer), _first_text(getattr(offer, 'product_name', '')) or 'Oferta base lista.'),
        ('market_research', 'Mercado', bool(niche), _first_text(getattr(niche, 'avatar_name', '')) or 'Insights de nicho generados.'),
        ('buyer_persona', 'Avatares', bool(avatars and avatars.avatars), _first_text((avatars.avatars or [{}])[0].get('name') if avatars and avatars.avatars else '') or 'Avatares listos.'),
        ('angles', 'Angulos', bool(artifacts.get('angles') and artifacts['angles'].status == 'done'), _first_text(getattr(artifacts.get('angles'), 'payload', {})) or 'Angulos de marketing generados.'),
        ('visual_identity', 'Visual', bool(artifacts.get('visual_identity') and artifacts['visual_identity'].status == 'done'), _first_text(getattr(artifacts.get('visual_identity'), 'payload', {})) or 'Identidad visual definida.'),
        ('mockups', 'Mockups', bool(artifacts.get('mockups') and artifacts['mockups'].status == 'done'), _first_text(getattr(artifacts.get('mockups'), 'payload', {})) or 'Mockups listos para produccion.'),
        ('ads_generator', 'Ads', bool(artifacts.get('ads_generator') and artifacts['ads_generator'].status == 'done'), _first_text(getattr(artifacts.get('ads_generator'), 'payload', {})) or 'Creativos de ads listos.'),
        ('landing_page', 'Landing', bool(artifacts.get('landing_page') and artifacts['landing_page'].status == 'done'), _first_text(getattr(artifacts.get('landing_page'), 'payload', {})) or 'Landing base generada.'),
        ('product_copies', 'Copies', bool(artifacts.get('product_copies') and artifacts['product_copies'].status == 'done'), _first_text(getattr(artifacts.get('product_copies'), 'payload', {})) or 'Copys principales listos.'),
        ('ad_copies', 'Ad Copies', bool(artifacts.get('ad_copies') and artifacts['ad_copies'].status == 'done'), _first_text(getattr(artifacts.get('ad_copies'), 'payload', {})) or 'Copys de anuncios listos.'),
        ('premium_scripts', 'Guiones', bool(artifacts.get('premium_scripts') and artifacts['premium_scripts'].status == 'done'), _first_text(getattr(artifacts.get('premium_scripts'), 'payload', {})) or 'Guiones de venta listos.'),
        ('ugc_realistic', 'UGC', bool(artifacts.get('ugc_realistic') and artifacts['ugc_realistic'].status == 'done'), _first_text(getattr(artifacts.get('ugc_realistic'), 'payload', {})) or 'Prompts UGC listos.'),
        ('product_generator', 'Producto', bool(outline), _first_text(getattr(outline, 'title', '')) or 'Estructura del producto generada.'),
        ('upsell_aov', 'Upsell', bool(revenue), _first_text(getattr(revenue, 'upsell', {})) or 'Estrategia AOV configurada.'),
        ('email_marketing', 'Email', bool(artifacts.get('email_marketing') and artifacts['email_marketing'].status == 'done'), _first_text(getattr(artifacts.get('email_marketing'), 'payload', {})) or 'Secuencias de email listas.'),
        ('global_export', 'Global', bool(artifacts.get('global_export') and artifacts['global_export'].status == 'done'), _first_text(getattr(artifacts.get('global_export'), 'payload', {})) or 'Checklist de expansion global listo.'),
    ]

    nodes = []
    active_assigned = False
    for key, label, done, summary in specs:
        if done:
            status = 'done'
        elif not active_assigned:
            status = 'active'
            active_assigned = True
        else:
            status = 'pending'
        nodes.append({'key': key, 'label': label, 'status': status, 'summary': summary[:140]})

    return nodes


# ──────────────────────────────────────────────
# PUBLIC
# ──────────────────────────────────────────────

LANDING_I18N = {'en': {'comp_badge': 'MagicBook vs. Traditional',
        'comp_col_challenge': 'Challenge',
        'comp_col_magic': 'With MagicBook',
        'comp_col_trad': 'Traditional Method',
        'comp_h1': 'Stop Wasting Time and Money.',
        'comp_h2': 'Do the Math.',
        'compare_rows': [{'challenge': 'Launch Time', 'magicbook': '15 Minutes', 'traditional': '4 to 8 Weeks'},
                         {'challenge': 'Tool Costs',
                          'magicbook': 'From $29 USD/mo (All Included)',
                          'traditional': '$300+ USD/mo (ClickFunnels, Canva, Stripe…)'},
                         {'challenge': 'Learning Curve',
                          'magicbook': 'Zero (AI does it, you edit)',
                          'traditional': 'High (Marketing, Design, Copy, Code)'},
                         {'challenge': 'Brand Coherence',
                          'magicbook': 'Perfect (Unique centralized DNA)',
                          'traditional': 'Hard (Information silos)'}],
        'cta_btn': 'Start Free Now',
        'cta_disc': 'No credit card · Cancel anytime',
        'cta_h1': 'Your Next Winning Product',
        'cta_h2': '15 Minutes',
        'cta_h2_post': ' Away.',
        'cta_h2_pre': 'Is ',
        'cta_sub': 'Join the new era of creators who automate their success.',
        'factory_assets': [{'delay': '.05s', 'icon': 'target', 'label': 'Offer'},
                           {'delay': '.12s', 'icon': 'users', 'label': 'Avatars'},
                           {'delay': '.19s', 'icon': 'search', 'label': 'Market'},
                           {'delay': '.26s', 'icon': 'image', 'label': 'Mockups'},
                           {'delay': '.33s', 'icon': 'layout', 'label': 'Landing'},
                           {'delay': '.40s', 'icon': 'book-open', 'label': 'Ebook'},
                           {'delay': '.47s', 'icon': 'mail', 'label': 'Emails'},
                           {'delay': '.54s', 'icon': 'megaphone', 'label': 'Ads'},
                           {'delay': '.61s', 'icon': 'video', 'label': 'Scripts'}],
        'factory_count': '16 assets generated',
        'factory_processing': 'Processing 16 modules…',
        'factory_prompt': 'I want to sell a finance course',
        'factory_ready': 'Ready',
        'features': [{'desc': 'Define WHAT you sell and why it’s unique. AI builds your Grand Promise.',
                      'icon': 'target',
                      'title': 'Irresistible Offer Modeling'},
                     {'desc': 'Know your customer better than themselves. Fears, desires and objections in seconds.',
                      'icon': 'users',
                      'title': 'Deep Avatars'},
                     {'desc': 'Detect trends, competition and ignored opportunities in your niche.',
                      'icon': 'search',
                      'title': 'Market Research'},
                     {'desc': 'Generate 5 differentiated sales angles ready to test in your ads.',
                      'icon': 'swords',
                      'title': 'Sales Angles'},
                     {'desc': 'HEX palette, typography and logo concept with perfect brand coherence.',
                      'icon': 'palette',
                      'title': 'Visual Identity'},
                     {'desc': 'Your product looks like $10k from day one. Visuals for mobile, tablet and print.',
                      'icon': 'image',
                      'title': 'Premium Mockups'},
                     {'desc': 'Your sales page ready to copy and paste. Optimized for conversion.',
                      'icon': 'layout',
                      'title': 'Landing Builder (HTML/JS)'},
                     {'desc': 'The factory writes your full product with structure, content and CTAs.',
                      'icon': 'book-open',
                      'title': 'Ebook Generator (40–80 pgs.)'},
                     {'desc': 'Persuasive text for checkout, payment page and welcome sequence.',
                      'icon': 'pen-line',
                      'title': 'Product Copy'},
                     {'desc': 'Ad creatives based on sales angles for Meta and TikTok.',
                      'icon': 'megaphone',
                      'title': 'Ads Generator'},
                     {'desc': 'Scripts for VSL or conversion reels with PAS and AIDA structure.',
                      'icon': 'video',
                      'title': 'Video Scripts'},
                     {'desc': 'Prompts and instructions for creator-style ads that convert.',
                      'icon': 'smartphone',
                      'title': 'Realistic UGC'},
                     {'desc': 'Abandoned cart, sales and onboarding sequences ready to copy.',
                      'icon': 'mail',
                      'title': 'Automated Email Marketing'},
                     {'desc': 'AI-generated upsell strategy and customer lifetime value maximization.',
                      'icon': 'trending-up',
                      'title': 'Upsells + AOV'},
                     {'desc': 'Multi-market: AR, MX, CO, CL, UY, BR, ES and more. All in one click.',
                      'icon': 'globe',
                      'title': 'Export & Sell Global'},
                     {'desc': 'Complete monetization plan with projections and scaling roadmap.',
                      'icon': 'bar-chart-2',
                      'title': 'Revenue Strategy'}],
        'hero_badge': 'AI · Marketing · Automation',
        'hero_cta_primary': 'Start Your Empire Now',
        'hero_cta_secondary': 'I already have an account',
        'hero_disclaimer': 'No credit card required · Ready in 30 seconds',
        'hero_h1a': 'MagicBook:',
        'hero_h1b': 'Your Info-Product',
        'hero_h1c': 'Factory',
        'hero_h1d': 'with AI in 15 min.',
        'hero_p1': 'From Idea to Complete Launch.',
        'hero_p2': 'No Analysis Paralysis. No Technical Stress.',
        'hero_p3': 'Everything in One Place.',
        'hero_social_label': 'entrepreneurs already automating',
        'page_title': 'MagicBook — Your Winning Info-Product Factory with AI in 15 Minutes',
        'prob_badge': 'Does this sound familiar?',
        'prob_callout_post': ', others are already scaling.',
        'prob_callout_pre': "While you're still",
        'prob_callout_styled': '“getting ready”',
        'prob_h1': 'How Long Have You Been',
        'prob_h2': '“Almost Ready”',
        'prob_h3': 'to Launch?',
        'prob_p': 'You have the knowledge. You have the idea. But reality paralyzes you: weeks lost trying to set up a '
                  'landing page, writing emails nobody reads, designing amateur-looking mockups, and burning money on '
                  'ads without a strategy.',
        'sol_badge': 'The Solution',
        'sol_h1': 'MagicBook: The Omnichannel System',
        'sol_h2': 'that Builds Your Business For You',
        'sol_p_a': 'MagicBook is not another generic chat. It’s a',
        'sol_p_b': 'that transforms a simple phrase (',
        'sol_p_bold': 'marketing engineering assistant',
        'sol_p_c': ') into a complete, validated, and fully-designed sales ecosystem.',
        'sol_p_em': '“I want to sell a finance course”',
        'sol_stat_label': 'of the work automated.',
        'sol_stat_sub1': 'You focus on the remaining 5%:',
        'sol_stat_sub2': 'launch and bill.',
        'steps_badge': 'How It Works',
        'steps_cta': 'Access All 16 Modules',
        'steps_h1a': '16 Steps.',
        'steps_h1b': 'One App.',
        'steps_h1c': 'Your Launch Ready.',
        'testi_badge': 'Social Proof',
        'testi_h1': 'Entrepreneurs Who Stopped',
        'testi_h2': '“Trying”',
        'testi_h3': 'and Started',
        'testi_h4': '“Selling”',
        'testimonials': [{'initials': 'LM',
                          'metric': '✅ $500 USD on her first launch',
                          'name': 'Laura M.',
                          'quote': 'I created my first Ebook and Landing in an afternoon. I already billed my first '
                                   '$500 USD. I can’t believe how simple it was.'},
                         {'initials': 'CV',
                          'metric': '✅ Launched on his first day of use',
                          'name': 'Carlos V.',
                          'quote': 'I had been “almost ready” to launch my course for 3 months. MagicBook did it in 20 '
                                   'minutes. The landing page turned out better than my competition’s.'},
                         {'initials': 'SR',
                          'metric': '✅ Saved $1,200 USD in consulting',
                          'name': 'Sofía R.',
                          'quote': 'The offer modeling it generates is better than what $500 consultants charged me. '
                                   'The speed difference is ridiculous.'}]},
 'es': {'comp_badge': 'MagicBook vs. Tradicional',
        'comp_col_challenge': 'Desafío',
        'comp_col_magic': 'Con MagicBook',
        'comp_col_trad': 'Método Tradicional',
        'comp_h1': 'Deja de Perder Tiempo y Dinero.',
        'comp_h2': 'Haz los Números.',
        'compare_rows': [{'challenge': 'Tiempo de Lanzamiento',
                          'magicbook': '15 Minutos',
                          'traditional': '4 a 8 Semanas'},
                         {'challenge': 'Costo de Herramientas',
                          'magicbook': 'Desde $29 USD/mes (Todo incluido)',
                          'traditional': '$300+ USD/mes (ClickFunnels, Canva, Stripe…)'},
                         {'challenge': 'Curva de Aprendizaje',
                          'magicbook': 'Cero (La IA lo hace, tú editas)',
                          'traditional': 'Alta (Marketing, Diseño, Copy, Code)'},
                         {'challenge': 'Coherencia de Marca',
                          'magicbook': 'Perfecta (ADN único centralizado)',
                          'traditional': 'Difícil (Silos de información)'}],
        'cta_btn': 'Empieza Gratis Ahora',
        'cta_disc': 'Sin tarjeta de crédito · Cancela cuando quieras',
        'cta_h1': 'Tu Próximo Producto Ganador',
        'cta_h2': '15 Minutos',
        'cta_h2_post': ' de Distancia.',
        'cta_h2_pre': 'Está a ',
        'cta_sub': 'Únete a la nueva era de creadores que automatizan su éxito.',
        'factory_assets': [{'delay': '.05s', 'icon': 'target', 'label': 'Oferta'},
                           {'delay': '.12s', 'icon': 'users', 'label': 'Avatares'},
                           {'delay': '.19s', 'icon': 'search', 'label': 'Mercado'},
                           {'delay': '.26s', 'icon': 'image', 'label': 'Mockups'},
                           {'delay': '.33s', 'icon': 'layout', 'label': 'Landing'},
                           {'delay': '.40s', 'icon': 'book-open', 'label': 'Ebook'},
                           {'delay': '.47s', 'icon': 'mail', 'label': 'Emails'},
                           {'delay': '.54s', 'icon': 'megaphone', 'label': 'Ads'},
                           {'delay': '.61s', 'icon': 'video', 'label': 'Guiones'}],
        'factory_count': '16 activos generados',
        'factory_processing': 'Procesando 16 módulos…',
        'factory_prompt': 'Quiero vender un curso de finanzas',
        'factory_ready': 'Listo',
        'features': [{'desc': 'Define QUÉ vendes y por qué es único en el mercado. La IA construye tu Gran Promesa.',
                      'icon': 'target',
                      'title': 'Modelado de Oferta Irresistible'},
                     {'desc': 'Conoce a tu cliente mejor que él mismo. Miedos, deseos y objeciones en segundos.',
                      'icon': 'users',
                      'title': 'Avatares Profundos'},
                     {'desc': 'Detecta tendencias, competencia y oportunidades ignoradas en tu nicho.',
                      'icon': 'search',
                      'title': 'Investigación de Mercado'},
                     {'desc': 'Genera 5 enfoques de venta diferenciados y listos para testear en tus ads.',
                      'icon': 'swords',
                      'title': 'Ángulos de Venta'},
                     {'desc': 'Paleta HEX, tipografías y concepto de logo con coherencia de marca perfecta.',
                      'icon': 'palette',
                      'title': 'Identidad Visual'},
                     {'desc': 'Tu producto se ve de $10k USD desde el día uno. Visuales para móvil, tablet e impreso.',
                      'icon': 'image',
                      'title': 'Mockups Premium'},
                     {'desc': 'Tu web de ventas lista para copiar y pegar. Optimizada para conversión.',
                      'icon': 'layout',
                      'title': 'Landing Builder (HTML/JS)'},
                     {'desc': 'La fábrica redacta tu producto completo con estructura, contenido y CTA.',
                      'icon': 'book-open',
                      'title': 'Ebook Generator (40–80 pág.)'},
                     {'desc': 'Textos persuasivos para checkout, página de pago y secuencia de bienvenida.',
                      'icon': 'pen-line',
                      'title': 'Copys de Producto'},
                     {'desc': 'Creativos publicitarios basados en ángulos de venta para Meta y TikTok.',
                      'icon': 'megaphone',
                      'title': 'Generador de Ads'},
                     {'desc': 'Scripts para VSL o reels de conversión con estructura PAS y AIDA.',
                      'icon': 'video',
                      'title': 'Guiones de Video'},
                     {'desc': 'Prompts e instrucciones para anuncios estilo creador que convierten.',
                      'icon': 'smartphone',
                      'title': 'UGC Realistas'},
                     {'desc': 'Secuencias de carrito abandonado, venta y onboarding listas para copiar.',
                      'icon': 'mail',
                      'title': 'Email Marketing Automático'},
                     {'desc': 'Estrategia de upsell y maximización del valor por cliente generada por IA.',
                      'icon': 'trending-up',
                      'title': 'Upsells + AOV'},
                     {'desc': 'Multi-mercado: AR, MX, CO, CL, UY, BR, ES y más. Todo en un clic.',
                      'icon': 'globe',
                      'title': 'Exportar y Vender Global'},
                     {'desc': 'Plan de monetización completo con proyecciones y escalado definido.',
                      'icon': 'bar-chart-2',
                      'title': 'Revenue Strategy'}],
        'hero_badge': 'IA · Marketing · Automatización',
        'hero_cta_primary': 'Empieza Tu Imperio Ahora',
        'hero_cta_secondary': 'Ya tengo cuenta',
        'hero_disclaimer': 'Sin tarjeta de crédito · Listo en 30 segundos',
        'hero_h1a': 'MagicBook:',
        'hero_h1b': 'Tu Fábrica de',
        'hero_h1c': 'Infoproductos',
        'hero_h1d': 'con IA en 15 min.',
        'hero_p1': 'De la Idea al Lanzamiento Completo.',
        'hero_p2': 'Sin Parálisis por Análisis. Sin Estrés Técnico.',
        'hero_p3': 'Todo en un Solo Lugar.',
        'hero_social_label': 'emprendedores ya automatizando',
        'page_title': 'MagicBook — Tu Fábrica de Infoproductos Ganadores con IA en 15 Minutos',
        'prob_badge': '¿Te suena familiar?',
        'prob_callout_post': ', otros ya están escalando.',
        'prob_callout_pre': 'Mientras tú sigues',
        'prob_callout_styled': '"\xa0preparándote\xa0"',
        'prob_h1': '¿Cuánto Tiempo Llevas',
        'prob_h2': '"\xa0Casi Listo\xa0"',
        'prob_h3': 'Para Lanzar?',
        'prob_p': 'Tienes el conocimiento. Tienes la idea. Pero la realidad te paraliza: semanas perdidas intentando '
                  'configurar una landing, escribiendo emails que nadie lee, diseñando mockups que parecen amateurs y '
                  'quemando dinero en anuncios sin estrategia.',
        'sol_badge': 'La Solución',
        'sol_h1': 'MagicBook: El Sistema Omnicanal',
        'sol_h2': 'que Crea Tu Negocio Por Ti',
        'sol_p_a': 'MagicBook no es otro chat genérico. Es un',
        'sol_p_b': 'que transforma una frase simple (',
        'sol_p_bold': 'asistente de ingeniería de marketing',
        'sol_p_c': ') en un ecosistema de ventas completo, validado y maquetado.',
        'sol_p_em': '“Quiero vender un curso de finanzas”',
        'sol_stat_label': 'del trabajo automatizado.',
        'sol_stat_sub1': 'Tú te enfocas en el 5% restante:',
        'sol_stat_sub2': 'lanzar y facturar.',
        'steps_badge': 'Cómo Funciona',
        'steps_cta': 'Acceder a los 16 Módulos',
        'steps_h1a': '16 Pasos.',
        'steps_h1b': 'Una Sola App.',
        'steps_h1c': 'Tu Lanzamiento Listo.',
        'testi_badge': 'Prueba Social',
        'testi_h1': 'Emprendedores que Dejaron de',
        'testi_h2': '"\xa0Intentar\xa0"',
        'testi_h3': 'y Empezaron a',
        'testi_h4': '"\xa0Vender\xa0"',
        'testimonials': [{'initials': 'LM',
                          'metric': '✅ $500 USD en su primer lanzamiento',
                          'name': 'Laura M.',
                          'quote': 'Creé mi primer Ebook y Landing en una tarde. Ya facturé mis primeros $500 USD. No '
                                   'puedo creer lo simple que fue.'},
                         {'initials': 'CV',
                          'metric': '✅ Lanzó en su primer día de uso',
                          'name': 'Carlos V.',
                          'quote': 'Llevaba 3 meses “casi listo” para lanzar mi curso. MagicBook lo hizo en 20 '
                                   'minutos. La landing quedó mejor que la de mi competencia.'},
                         {'initials': 'SR',
                          'metric': '✅ Ahorró $1,200 USD en consultoría',
                          'name': 'Sofía R.',
                          'quote': 'El modelado de oferta que genera es mejor que lo que me cobraban $500 consultores. '
                                   'Es ridícula la diferencia de velocidad.'}]},
 'pt': {'comp_badge': 'MagicBook vs. Tradicional',
        'comp_col_challenge': 'Desafio',
        'comp_col_magic': 'Com MagicBook',
        'comp_col_trad': 'Método Tradicional',
        'comp_h1': 'Pare de Perder Tempo e Dinheiro.',
        'comp_h2': 'Faça as Contas.',
        'compare_rows': [{'challenge': 'Tempo de Lançamento',
                          'magicbook': '15 Minutos',
                          'traditional': '4 a 8 Semanas'},
                         {'challenge': 'Custo de Ferramentas',
                          'magicbook': 'A partir de $29 USD/mês (Tudo incluído)',
                          'traditional': '$300+ USD/mês (ClickFunnels, Canva, Stripe…)'},
                         {'challenge': 'Curva de Aprendizado',
                          'magicbook': 'Zero (A IA faz, você edita)',
                          'traditional': 'Alta (Marketing, Design, Copy, Código)'},
                         {'challenge': 'Coerência de Marca',
                          'magicbook': 'Perfeita (DNA único centralizado)',
                          'traditional': 'Difícil (Silos de informação)'}],
        'cta_btn': 'Começar Grátis Agora',
        'cta_disc': 'Sem cartão de crédito · Cancele quando quiser',
        'cta_h1': 'Seu Próximo Produto Vencedor Está a',
        'cta_h2': '15 Minutos',
        'cta_h2_post': ' de Distância.',
        'cta_h2_pre': '',
        'cta_sub': 'Junte-se à nova era de criadores que automatizam seu sucesso.',
        'factory_assets': [{'delay': '.05s', 'icon': 'target', 'label': 'Oferta'},
                           {'delay': '.12s', 'icon': 'users', 'label': 'Avatares'},
                           {'delay': '.19s', 'icon': 'search', 'label': 'Mercado'},
                           {'delay': '.26s', 'icon': 'image', 'label': 'Mockups'},
                           {'delay': '.33s', 'icon': 'layout', 'label': 'Landing'},
                           {'delay': '.40s', 'icon': 'book-open', 'label': 'Ebook'},
                           {'delay': '.47s', 'icon': 'mail', 'label': 'Emails'},
                           {'delay': '.54s', 'icon': 'megaphone', 'label': 'Ads'},
                           {'delay': '.61s', 'icon': 'video', 'label': 'Scripts'}],
        'factory_count': '16 ativos gerados',
        'factory_processing': 'Processando 16 módulos…',
        'factory_prompt': 'Quero vender um curso de finanças',
        'factory_ready': 'Pronto',
        'features': [{'desc': 'Defina O QUE você vende e por que é único. A IA constrói sua Grande Promessa.',
                      'icon': 'target',
                      'title': 'Modelagem de Oferta Irresistível'},
                     {'desc': 'Conheça seu cliente melhor que ele mesmo. Medos, desejos e objeções em segundos.',
                      'icon': 'users',
                      'title': 'Avatares Profundos'},
                     {'desc': 'Detecte tendências, concorrência e oportunidades ignoradas no seu nicho.',
                      'icon': 'search',
                      'title': 'Pesquisa de Mercado'},
                     {'desc': 'Gere 5 abordagens de venda diferenciadas prontas para testar em seus anúncios.',
                      'icon': 'swords',
                      'title': 'Ângulos de Venda'},
                     {'desc': 'Paleta HEX, tipografias e conceito de logo com coerência de marca perfeita.',
                      'icon': 'palette',
                      'title': 'Identidade Visual'},
                     {'desc': 'Seu produto parece valer $10k desde o primeiro dia. Visuais para celular, tablet e '
                              'impresso.',
                      'icon': 'image',
                      'title': 'Mockups Premium'},
                     {'desc': 'Sua página de vendas pronta para copiar e colar. Otimizada para conversão.',
                      'icon': 'layout',
                      'title': 'Landing Builder (HTML/JS)'},
                     {'desc': 'A fábrica escreve seu produto completo com estrutura, conteúdo e CTAs.',
                      'icon': 'book-open',
                      'title': 'Gerador de Ebook (40–80 págs.)'},
                     {'desc': 'Textos persuasivos para checkout, página de pagamento e sequência de boas-vindas.',
                      'icon': 'pen-line',
                      'title': 'Copys de Produto'},
                     {'desc': 'Criativos publicitários baseados em ângulos de venda para Meta e TikTok.',
                      'icon': 'megaphone',
                      'title': 'Gerador de Anúncios'},
                     {'desc': 'Scripts para VSL ou reels de conversão com estrutura PAS e AIDA.',
                      'icon': 'video',
                      'title': 'Roteiros de Vídeo'},
                     {'desc': 'Prompts e instruções para anúncios estilo criador que convertem.',
                      'icon': 'smartphone',
                      'title': 'UGC Realistas'},
                     {'desc': 'Sequências de carrinho abandonado, venda e onboarding prontas para copiar.',
                      'icon': 'mail',
                      'title': 'Email Marketing Automático'},
                     {'desc': 'Estratégia de upsell e maximização do valor por cliente gerada por IA.',
                      'icon': 'trending-up',
                      'title': 'Upsells + AOV'},
                     {'desc': 'Multi-mercado: AR, MX, CO, CL, UY, BR, ES e mais. Tudo em um clique.',
                      'icon': 'globe',
                      'title': 'Exportar e Vender Global'},
                     {'desc': 'Plano de monetização completo com projeções e escalonamento definido.',
                      'icon': 'bar-chart-2',
                      'title': 'Estratégia de Revenue'}],
        'hero_badge': 'IA · Marketing · Automação',
        'hero_cta_primary': 'Começe Seu Império Agora',
        'hero_cta_secondary': 'Já tenho uma conta',
        'hero_disclaimer': 'Sem cartão de crédito · Pronto em 30 segundos',
        'hero_h1a': 'MagicBook:',
        'hero_h1b': 'Sua Fábrica de',
        'hero_h1c': 'Infoprodutos',
        'hero_h1d': 'com IA em 15 min.',
        'hero_p1': 'Da Ideia ao Lançamento Completo.',
        'hero_p2': 'Sem Paralisia por Análise. Sem Estresse Técnico.',
        'hero_p3': 'Tudo em Um Só Lugar.',
        'hero_social_label': 'empreendedores já automatizando',
        'page_title': 'MagicBook — Sua Fábrica de Infoprodutos Vencedores com IA em 15 Minutos',
        'prob_badge': 'Isso parece familiar?',
        'prob_callout_post': ', outros já estão escalando.',
        'prob_callout_pre': 'Enquanto você ainda está',
        'prob_callout_styled': '“se preparando”',
        'prob_h1': 'Há Quanto Tempo Você Está',
        'prob_h2': '“Quase Pronto”',
        'prob_h3': 'para Lançar?',
        'prob_p': 'Você tem o conhecimento. Tem a ideia. Mas a realidade te paralisa: semanas perdidas tentando '
                  'configurar uma landing page, escrevendo emails que ninguém lê, criando mockups amadores e queimando '
                  'dinheiro em anúncios sem estratégia.',
        'sol_badge': 'A Solução',
        'sol_h1': 'MagicBook: O Sistema Omnicanal',
        'sol_h2': 'que Constrói Seu Negócio Por Você',
        'sol_p_a': 'MagicBook não é mais um chat genérico. É um',
        'sol_p_b': 'que transforma uma frase simples (',
        'sol_p_bold': 'assistente de engenharia de marketing',
        'sol_p_c': ') em um ecossistema de vendas completo, validado e formatado.',
        'sol_p_em': '“Quero vender um curso de finanças”',
        'sol_stat_label': 'do trabalho automatizado.',
        'sol_stat_sub1': 'Você foca nos 5% restantes:',
        'sol_stat_sub2': 'lançar e faturar.',
        'steps_badge': 'Como Funciona',
        'steps_cta': 'Acessar os 16 Módulos',
        'steps_h1a': '16 Passos.',
        'steps_h1b': 'Um Só App.',
        'steps_h1c': 'Seu Lançamento Pronto.',
        'testi_badge': 'Prova Social',
        'testi_h1': 'Empreendedores que Pararam de',
        'testi_h2': '“Tentar”',
        'testi_h3': 'e Começaram a',
        'testi_h4': '“Vender”',
        'testimonials': [{'initials': 'LM',
                          'metric': '✅ $500 USD no seu primeiro lançamento',
                          'name': 'Laura M.',
                          'quote': 'Criei meu primeiro Ebook e Landing em uma tarde. Já faturei meus primeiros $500 '
                                   'USD. Não consigo acreditar como foi simples.'},
                         {'initials': 'CV',
                          'metric': '✅ Lançou no primeiro dia de uso',
                          'name': 'Carlos V.',
                          'quote': 'Fiquei 3 meses “quase pronto” para lançar meu curso. O MagicBook fez em 20 '
                                   'minutos. A landing ficou melhor que a da minha concorrência.'},
                         {'initials': 'SR',
                          'metric': '✅ Economizou $1.200 USD em consultoria',
                          'name': 'Sofia R.',
                          'quote': 'A modelagem de oferta que gera é melhor do que o que consultores de $500 me '
                                   'cobravam. A diferença de velocidade é absurda.'}]}}


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')

        lang = (get_language() or 'en')[:2]
        lp = LANDING_I18N.get(lang, LANDING_I18N['en'])
        return render(request, 'home.html', {'lp': lp})


# ──────────────────────────────────────────────
# DASHBOARD (requires login)
# ──────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'core/dashboard.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).select_related(
            'niche_analysis', 'offer_structure', 'revenue_strategy', 'product_outline', 'copy_library', 'avatar_profile'
        ).prefetch_related('artifacts')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        projects_qs = ctx['projects']
        enrollment = PlanAEnrollment.objects.filter(user=self.request.user).first()
        has_projects = projects_qs.exists()
        first_project = projects_qs.first()

        step1_done = bool(enrollment and enrollment.credentials_email_sent_at)
        step2_done = bool(enrollment and enrollment.first_login_at)
        step3_done = bool(enrollment and (enrollment.first_project_launched_at or has_projects))

        for project in projects_qs:
            launch_map_nodes = _build_launch_map_nodes(project)
            project.launch_map_nodes = launch_map_nodes
            project.launch_done_count = sum(1 for node in launch_map_nodes if node['status'] == 'done')
            project.launch_progress = int((project.launch_done_count / 16) * 100)
            pending_labels = [node['label'] for node in launch_map_nodes if node['status'] != 'done']
            if pending_labels:
                preview = pending_labels[:2]
                suffix = '...' if len(pending_labels) > 2 else ''
                project.missing_hint = f"Falta {', '.join(preview)}{suffix}"
            else:
                project.missing_hint = 'Listo para lanzar'

            thumbnail_url = ''
            for artifact in project.artifacts.all():
                if artifact.status != 'done':
                    continue
                thumbnail_url = _find_first_image_url(artifact.payload)
                if thumbnail_url:
                    break
            project.thumbnail_url = thumbnail_url

        quickstart_steps = [
            {
                'label': 'Email de acceso recibido',
                'hint': 'Confirma que tienes tus links directos a la app y a crear proyecto.',
                'done': step1_done,
            },
            {
                'label': 'Cuenta activa en la app',
                'hint': 'Tu sesión y entorno de Plan A ya están operativos.',
                'done': step2_done,
            },
            {
                'label': 'Primer producto lanzado',
                'hint': 'Crea tu primer proyecto para encender la fábrica de contenido.',
                'done': step3_done,
            },
        ]

        if not step1_done:
            primary_cta = {
                'label': 'Completar onboarding de Plan A',
                'url': 'accounts:plan_a_onboarding',
                'helper': 'Reenvía credenciales y revisa el flujo de activación en 1 minuto.',
            }
        elif not has_projects:
            primary_cta = {
                'label': 'Crear mi primer proyecto',
                'url': 'core:project_create',
                'helper': 'Empieza con tu nicho y deja que la IA construya tu oferta.',
            }
        elif first_project and first_project.completion_percentage < 100:
            primary_cta = {
                'label': 'Continuar proyecto activo',
                'url': 'core:project_detail',
                'args': [first_project.pk],
                'helper': 'Retoma el módulo pendiente para completar el flujo base.',
            }
        else:
            primary_cta = {
                'label': 'Ir a la Fábrica 16',
                'url': 'core:project_factory',
                'args': [first_project.pk] if first_project else [],
                'helper': 'Escala con ads, landing, scripts y exportación global.',
            }

        ctx['quickstart_steps'] = quickstart_steps
        ctx['quickstart_done_count'] = sum(1 for item in quickstart_steps if item['done'])
        ctx['primary_cta'] = primary_cta
        ctx['dashboard_stats'] = {
            'active_projects': projects_qs.count(),
            'infoproducts_generated': sum(1 for p in projects_qs if hasattr(p, 'product_outline')),
            'launches_ready': sum(1 for p in projects_qs if getattr(p, 'launch_done_count', 0) >= 16),
        }
        ctx['dashboard_phases'] = DASHBOARD_PHASES
        return ctx


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
        _sync_workflow_from_project(project)
        has_niche = hasattr(project, 'niche_analysis')
        has_offer = hasattr(project, 'offer_structure')
        has_revenue = hasattr(project, 'revenue_strategy')
        has_outline = hasattr(project, 'product_outline')
        has_copy = hasattr(project, 'copy_library')

        ctx['has_niche'] = has_niche
        ctx['has_offer'] = has_offer
        ctx['has_revenue'] = has_revenue
        ctx['has_outline'] = has_outline
        ctx['has_copy'] = has_copy
        ctx['step_labels'] = STEP_LABELS
        ctx['step_labels_json'] = json.dumps(STEP_LABELS)
        # Build a dict {chapter_number: word_count} for written chapters
        written_chapters = {
            ch.chapter_number: ch.word_count
            for ch in project.chapter_contents.filter(status='done')
        }
        chapter_contents = {
            ch.chapter_number: ch.content
            for ch in project.chapter_contents.filter(status='done')
        }
        ctx['written_chapters'] = written_chapters
        ctx['chapter_contents'] = chapter_contents
        ctx['written_count'] = len(written_chapters)
        undo_available_chapters = list(
            ChapterRewriteHistory.objects.filter(
                project=project,
                undone_at__isnull=True,
            ).values_list('chapter_number', flat=True).distinct()
        )
        ctx['undo_available_chapters'] = undo_available_chapters

        if not has_niche:
            next_step = {
                'title': 'Siguiente paso recomendado: Análisis de Nicho',
                'description': 'Empieza por aquí para desbloquear oferta, revenue y resto del flujo.',
                'action_type': 'generate',
                'module': 'niche',
                'button': 'Generar Análisis de Nicho',
            }
        elif not has_offer:
            next_step = {
                'title': 'Siguiente paso recomendado: Oferta Irresistible',
                'description': 'Define precio, bonos y garantía para preparar la venta.',
                'action_type': 'generate',
                'module': 'offer',
                'button': 'Generar Oferta',
            }
        elif not has_revenue:
            next_step = {
                'title': 'Siguiente paso recomendado: Revenue Management',
                'description': 'Activa order bump y upsell para subir el ticket promedio.',
                'action_type': 'generate',
                'module': 'revenue',
                'button': 'Generar Revenue',
            }
        elif not has_outline:
            next_step = {
                'title': 'Siguiente paso recomendado: Índice del Infoproducto',
                'description': 'Genera la estructura completa para empezar a redactar capítulos.',
                'action_type': 'generate',
                'module': 'outline',
                'button': 'Generar Índice',
            }
        elif not has_copy:
            next_step = {
                'title': 'Siguiente paso recomendado: Biblioteca de Copies',
                'description': 'Crea headlines y copies listos para tus anuncios y landing.',
                'action_type': 'generate',
                'module': 'copy',
                'button': 'Generar Copies',
            }
        else:
            next_step = {
                'title': 'Flujo base completo',
                'description': 'Tu base está lista. Ahora escala en la Fábrica 16.',
                'action_type': 'url',
                'url_name': 'core:project_factory',
                'button': 'Abrir Fábrica 16',
            }

        ctx['next_step'] = next_step

        suggestions = []
        if has_offer:
            offer = project.offer_structure
            bonus_count = len(offer.bonuses or [])
            if bonus_count < 2:
                suggestions.append({
                    'title': 'Oferta mejorable detectada',
                    'detail': 'Agrega al menos 2 bonuses para subir valor percibido y conversion.',
                    'module': 'offer',
                    'cta': 'Aplicar mejora de oferta',
                })

        if has_outline and not has_copy:
            suggestions.append({
                'title': 'Activa copys para vender mas rapido',
                'detail': 'Ya tienes estructura: genera headlines y hooks para anuncios en un clic.',
                'module': 'copy',
                'cta': 'Generar copys sugeridos',
            })

        if has_offer and not has_revenue:
            suggestions.append({
                'title': 'Monetizacion incompleta',
                'detail': 'Falta Order Bump + Upsell para elevar ticket promedio.',
                'module': 'revenue',
                'cta': 'Completar revenue ahora',
            })

        ctx['suggestions'] = suggestions[:2]
        ctx['launch_map_nodes'] = _build_launch_map_nodes(project)
        ctx['launch_done_count'] = sum(1 for item in ctx['launch_map_nodes'] if item['status'] == 'done')
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
            _sync_workflow_from_project(project)

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

        artifact_step_map = {
            'angles': 4,
            'visual_identity': 5,
            'mockups': 6,
            'ads_generator': 7,
            'landing_page': 8,
            'product_copies': 9,
            'ad_copies': 10,
            'premium_scripts': 10,
            'ugc_realistic': 11,
            'email_marketing': 14,
            'global_export': 15,
        }
        target_step = artifact_step_map.get(artifact_type)
        if target_step:
            for previous_step in range(1, target_step):
                is_completed, _ = _step_content_snapshot(project, previous_step)
                if not is_completed:
                    return JsonResponse(
                        {
                            'success': False,
                            'error': f'Paso bloqueado: completa el paso {previous_step} antes de generar este módulo.'
                        },
                        status=400,
                    )

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
            _sync_workflow_from_project(project)

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
            _sync_workflow_from_project(project)
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
            _sync_workflow_from_project(project)

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
            _sync_workflow_from_project(project)
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
            _sync_workflow_from_project(project)

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
            _sync_workflow_from_project(project)

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
            _sync_workflow_from_project(project)

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
            _sync_workflow_from_project(project)

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
            _sync_workflow_from_project(project)

            return JsonResponse({
                'success': True,
                'chapter_number': chapter_num,
                'title': chapter_data.get('title', ''),
                'word_count': word_count,
                'content': content,
            })

        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class RewriteParagraphView(LoginRequiredMixin, View):
    """POST /api/rewrite/paragraph/<pk>/ → rewrites a single paragraph with IA."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

        paragraph = (payload.get('paragraph') or '').strip()
        tone = (payload.get('tone') or 'mas claro').strip()
        context = (payload.get('context') or '').strip()

        if not paragraph:
            return JsonResponse({'success': False, 'error': 'Falta el párrafo a reescribir.'}, status=400)

        try:
            service = AIService(model=project.ai_model, brand_voice=project.brand_voice)
            rewritten = service.rewrite_paragraph(
                paragraph=paragraph,
                tone=tone,
                context=context,
            )
            return JsonResponse({'success': True, 'rewritten': rewritten})
        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class RewriteChapterView(LoginRequiredMixin, View):
    """POST /api/rewrite/chapter/<pk>/ → rewrites full chapter content with IA."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

        chapter_num = payload.get('chapter_num')
        chapter_numbers = payload.get('chapter_numbers')
        tone = (payload.get('tone') or 'mas claro y directo').strip()
        scope = (payload.get('scope') or 'full').strip().lower()
        shorten_percent = payload.get('shorten_percent', 0)

        if scope not in {'full', 'intro'}:
            return JsonResponse({'success': False, 'error': 'scope debe ser "full" o "intro".'}, status=400)

        try:
            shorten_percent = int(shorten_percent)
        except (TypeError, ValueError):
            shorten_percent = 0
        shorten_percent = max(0, min(shorten_percent, 60))

        requested_numbers = []
        if isinstance(chapter_num, int):
            requested_numbers.append(chapter_num)
        if isinstance(chapter_numbers, list):
            requested_numbers.extend([n for n in chapter_numbers if isinstance(n, int)])

        requested_numbers = sorted(set(requested_numbers))
        if not requested_numbers:
            return JsonResponse(
                {'success': False, 'error': 'Debes indicar chapter_num o chapter_numbers válidos.'},
                status=400,
            )

        chapters = list(
            ChapterContent.objects.filter(
                project=project,
                chapter_number__in=requested_numbers,
                status='done',
            ).order_by('chapter_number')
        )
        found_numbers = {c.chapter_number for c in chapters}
        missing_numbers = [n for n in requested_numbers if n not in found_numbers]

        if not chapters:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Ningún capítulo solicitado está escrito todavía.'
                },
                status=400,
            )

        try:
            service = AIService(model=project.ai_model, brand_voice=project.brand_voice)
            rewritten_items = []
            for chapter in chapters:
                content_to_rewrite = chapter.content
                scope_for_call = scope
                if scope == 'intro':
                    blocks = [b.strip() for b in re.split(r'\n\s*\n', chapter.content or '') if b.strip()]
                    intro_blocks = blocks[:2] if len(blocks) >= 2 else blocks
                    content_to_rewrite = '\n\n'.join(intro_blocks)
                    scope_for_call = 'intro'

                rewritten_part = service.rewrite_chapter_content(
                    chapter_title=chapter.title or f'Capítulo {chapter.chapter_number}',
                    original_content=content_to_rewrite,
                    tone=tone,
                    context=f'Proyecto: {project.title or project.niche_input}',
                    shorten_percent=shorten_percent,
                    scope=scope_for_call,
                )

                if scope == 'intro':
                    blocks = [b.strip() for b in re.split(r'\n\s*\n', chapter.content or '') if b.strip()]
                    remaining = blocks[2:] if len(blocks) > 2 else []
                    final_content = rewritten_part.strip()
                    if remaining:
                        final_content += '\n\n' + '\n\n'.join(remaining)
                else:
                    final_content = rewritten_part.strip()

                ChapterRewriteHistory.objects.create(
                    project=project,
                    chapter_number=chapter.chapter_number,
                    previous_content=chapter.content,
                    previous_word_count=chapter.word_count,
                    tone=tone,
                    scope=scope,
                    shorten_percent=shorten_percent,
                )

                chapter.content = final_content
                chapter.word_count = len(final_content.split())
                chapter.save(update_fields=['content', 'word_count', 'updated_at'])
                _sync_workflow_from_project(project)

                rewritten_items.append(
                    {
                        'chapter_number': chapter.chapter_number,
                        'title': chapter.title,
                        'word_count': chapter.word_count,
                        'rewritten': final_content,
                    }
                )

            response_data = {
                'success': True,
                'tone': tone,
                'scope': scope,
                'shorten_percent': shorten_percent,
                'rewritten_items': rewritten_items,
                'missing_chapters': missing_numbers,
            }
            if len(rewritten_items) == 1:
                single = rewritten_items[0]
                response_data.update(
                    {
                        'chapter_number': single['chapter_number'],
                        'title': single['title'],
                        'word_count': single['word_count'],
                        'rewritten': single['rewritten'],
                    }
                )
            return JsonResponse(response_data)
        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)


class UndoChapterRewriteView(LoginRequiredMixin, View):
    """POST /api/rewrite/chapter/<pk>/undo/ → restores last rewrite snapshot."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

        chapter_num = payload.get('chapter_num')
        if not isinstance(chapter_num, int):
            return JsonResponse({'success': False, 'error': 'Debes indicar chapter_num como entero.'}, status=400)

        chapter = ChapterContent.objects.filter(
            project=project,
            chapter_number=chapter_num,
            status='done',
        ).first()
        if not chapter:
            return JsonResponse({'success': False, 'error': 'Ese capítulo no existe o no está escrito.'}, status=400)

        history_item = ChapterRewriteHistory.objects.filter(
            project=project,
            chapter_number=chapter_num,
            undone_at__isnull=True,
        ).order_by('-created_at').first()
        if not history_item:
            return JsonResponse({'success': False, 'error': 'No hay historial para deshacer en este capítulo.'}, status=400)

        chapter.content = history_item.previous_content
        chapter.word_count = history_item.previous_word_count
        chapter.save(update_fields=['content', 'word_count', 'updated_at'])
        _sync_workflow_from_project(project)

        history_item.undone_at = timezone.now()
        history_item.save(update_fields=['undone_at'])

        has_more = ChapterRewriteHistory.objects.filter(
            project=project,
            chapter_number=chapter_num,
            undone_at__isnull=True,
        ).exists()

        return JsonResponse(
            {
                'success': True,
                'chapter_number': chapter_num,
                'word_count': chapter.word_count,
                'restored': chapter.content,
                'can_undo_again': has_more,
            }
        )



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
                    _sync_workflow_from_project(_project)
                    yield f"data: {json.dumps({'type': 'chapter_done', 'chapter': i, 'total': total, 'title': ch_data.get('title', ''), 'word_count': word_count})}\n\n"

                except Exception as exc:
                    yield f"data: {json.dumps({'type': 'chapter_error', 'chapter': i, 'error': str(exc)})}\n\n"

            # All chapters done — mark project complete and emit final event
            total_words = sum(
                ch.word_count for ch in _CC.objects.filter(project=_project, status='done')
            )
            _project.status = 'complete'
            _project.save(update_fields=['status'])
            _sync_workflow_from_project(_project)

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


# ──────────────────────────────────────────────────────────────────────────────
# Step 12: Fábrica de Libros — BookContent CRUD + AI enhance
# ──────────────────────────────────────────────────────────────────────────────

class BookContentLoadView(LoginRequiredMixin, View):
    """
    GET /api/book-content/<int:pk>/load/
    Returns all BookContent rows for the project as JSON.
    """

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        chapters = list(
            BookContent.objects.filter(project=project)
            .values('chapter_number', 'chapter_title', 'content', 'word_count', 'is_reviewed')
            .order_by('chapter_number')
        )
        total_words = sum(c['word_count'] for c in chapters)
        return JsonResponse({'success': True, 'chapters': chapters, 'total_words': total_words})


class BookContentSaveView(LoginRequiredMixin, View):
    """
    POST /api/book-content/<int:pk>/save/
    Body JSON: { chapter_number, chapter_title, content, is_reviewed? }
    Upserts a single BookContent row and recalculates word_count.
    """

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

        chapter_number = data.get('chapter_number')
        chapter_title = (data.get('chapter_title') or '').strip()
        content = data.get('content', '')
        is_reviewed = bool(data.get('is_reviewed', False))

        if not chapter_number or not isinstance(chapter_number, int):
            return JsonResponse({'success': False, 'error': 'chapter_number requerido'}, status=400)

        word_count = len(content.split()) if content else 0

        if is_reviewed and word_count < 800:
            return JsonResponse(
                {'success': False, 'error': f'El capítulo necesita mínimo 800 palabras para marcarse como revisado (tiene {word_count}).'},
                status=400,
            )

        obj, _ = BookContent.objects.update_or_create(
            project=project,
            chapter_number=chapter_number,
            defaults={
                'chapter_title': chapter_title,
                'content': content,
                'word_count': word_count,
                'is_reviewed': is_reviewed,
            },
        )

        all_chapters = BookContent.objects.filter(project=project)
        total_words = sum(c.word_count for c in all_chapters)

        return JsonResponse({
            'success': True,
            'chapter_number': chapter_number,
            'word_count': word_count,
            'total_words': total_words,
        })


class BookContentEnhanceView(LoginRequiredMixin, View):
    """
    POST /api/book-content/<int:pk>/enhance/
    Body JSON: { chapter_number, selected_text, action }
    action: 'expand' | 'tone' | 'example'
    Returns: { success, enhanced_text }
    """

    ACTION_PROMPTS = {
        'expand': (
            "Eres un editor experto en infoproductos digitales. "
            "El usuario ha seleccionado el siguiente fragmento de su libro. "
            "Expándelo con más detalle, ejemplos concretos y profundidad narrativa. "
            "Mantén el mismo tono y estilo. Responde solo con el texto expandido.\n\n"
            "FRAGMENTO:\n{text}"
        ),
        'tone': (
            "Eres un editor experto. Reescribe el siguiente fragmento haciéndolo más dinámico, "
            "conversacional y directo. Como si lo dijera un mentor que habla con su alumno. "
            "Responde solo con el texto reescrito.\n\n"
            "FRAGMENTO:\n{text}"
        ),
        'example': (
            "Eres un escritor de infoproductos. Al siguiente fragmento, añade una analogía poderosa "
            "o un caso de estudio real que ilustre el concepto. Intégralo de forma natural. "
            "Responde solo con el fragmento enriquecido con el ejemplo.\n\n"
            "FRAGMENTO:\n{text}"
        ),
    }

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

        selected_text = (data.get('selected_text') or '').strip()
        action = data.get('action', 'expand')

        if not selected_text:
            return JsonResponse({'success': False, 'error': 'selected_text requerido'}, status=400)
        if action not in self.ACTION_PROMPTS:
            return JsonResponse({'success': False, 'error': 'action inválido'}, status=400)
        if len(selected_text) > 4000:
            return JsonResponse({'success': False, 'error': 'Fragmento demasiado largo (máx 4000 chars)'}, status=400)

        prompt = self.ACTION_PROMPTS[action].format(text=selected_text)

        try:
            from .services import AIService
            ai = AIService(project)
            enhanced = ai.complete(prompt, max_tokens=1200)
        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=500)

        return JsonResponse({'success': True, 'enhanced_text': enhanced})
