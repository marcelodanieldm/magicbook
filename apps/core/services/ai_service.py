"""AI service layer that centralizes model calls and prompt orchestration."""

import json
import re
from django.conf import settings
from openai import OpenAI

from .prompts import (
    NICHE_ANALYSIS_SYSTEM_PROMPT,
    NICHE_ANALYSIS_USER_TEMPLATE,
    OFFER_SYSTEM_PROMPT,
    OFFER_USER_TEMPLATE,
    REVENUE_SYSTEM_PROMPT,
    REVENUE_USER_TEMPLATE,
    OUTLINE_SYSTEM_PROMPT,
    OUTLINE_USER_TEMPLATE,
    COPY_SYSTEM_PROMPT,
    COPY_USER_TEMPLATE,
    FULL_GENERATION_SYSTEM_PROMPT,
    FULL_GENERATION_USER_TEMPLATE,
    CHAPTER_WRITER_SYSTEM_PROMPT,
    CHAPTER_WRITER_USER_TEMPLATE,
    BRAND_VOICE_PERSONAS,
    apply_brand_voice,
)

# Claude models use a different client, so import it lazily and safely.
try:
    import anthropic as _anthropic_lib
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

# Maps prose model identifiers to the Anthropic call path.
_CLAUDE_MODELS = {'claude-3-5-sonnet-20241022'}


class AIService:
    """
    Service layer for all AI API interactions.

    Supports two model families:
    - OpenAI (gpt-4o, etc.)  → used for structured JSON generation
    - Anthropic Claude       → used for creative prose (chapter writing)

    The project's `ai_model` field controls which model is used per project.
    All JSON-generation modules always use OpenAI for reliability.
    The chapter writer uses the project's chosen model.
    """

    def __init__(self, model: str = None, brand_voice: str = 'mentor'):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.json_model = getattr(settings, 'AI_MODEL', 'gpt-4o')
        # Prose model can be overridden per-project (stored in Project.ai_model)
        self.prose_model = model or self.json_model
        self.brand_voice = brand_voice

        if _ANTHROPIC_AVAILABLE and hasattr(settings, 'ANTHROPIC_API_KEY'):
            self.anthropic_client = _anthropic_lib.Anthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            self.anthropic_client = None

    # ------------------------------------------------------------------
    # Low-level callers
    # ------------------------------------------------------------------
    def _call_openai_json(self, system_prompt: str, user_message: str,
                          temperature: float = 0.8) -> str:
        """OpenAI call with JSON mode enforced — for all 4 strategy modules."""
        response = self.openai_client.chat.completions.create(
            model=self.json_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def _call_prose(self, system_prompt: str, user_message: str,
                    temperature: float = 0.85) -> str:
        """
        Prose call — uses Claude if available and selected, otherwise OpenAI.
        Returns plain text (Markdown), NOT JSON.
        """
        if (self.prose_model in _CLAUDE_MODELS
                and self.anthropic_client is not None):
            msg = self.anthropic_client.messages.create(
                model=self.prose_model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return msg.content[0].text
        else:
            # Fallback: OpenAI without JSON mode (free-form Markdown)
            response = self.openai_client.chat.completions.create(
                model=self.prose_model if self.prose_model not in _CLAUDE_MODELS
                      else self.json_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_message},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content

    # Keep backward-compatible alias used by old views
    def _call(self, system_prompt: str, user_message: str,
              temperature: float = 0.8) -> str:
        return self._call_openai_json(system_prompt, user_message, temperature)

    def _parse_json(self, raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', raw)
            if match:
                return json.loads(match.group(1))
            raise ValueError(
                f"No se pudo parsear la respuesta de la IA. "
                f"Primeros 300 chars: {raw[:300]}"
            )

    def _with_voice(self, base_prompt: str) -> str:
        """Inject brand voice into any system prompt."""
        return apply_brand_voice(base_prompt, self.brand_voice)

    # ------------------------------------------------------------------
    # MÓDULO 1: Análisis de Nicho
    # ------------------------------------------------------------------
    def analyze_niche(self, niche_input: str) -> dict:
        system = self._with_voice(NICHE_ANALYSIS_SYSTEM_PROMPT)
        user_msg = NICHE_ANALYSIS_USER_TEMPLATE.format(niche=niche_input)
        raw = self._call_openai_json(system, user_msg, temperature=0.85)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data

    # ------------------------------------------------------------------
    # MÓDULO 2: Estructura de Oferta
    # ------------------------------------------------------------------
    def generate_offer(self, niche_input: str, niche_data: dict) -> dict:
        pains_text   = '\n'.join(f"- {p}" for p in niche_data.get('pains', [])[:3])
        desires_text = '\n'.join(f"- {d}" for d in niche_data.get('desires', [])[:3])
        system = self._with_voice(OFFER_SYSTEM_PROMPT)
        user_msg = OFFER_USER_TEMPLATE.format(
            niche=niche_input,
            avatar=niche_data.get('avatar_name', 'Avatar ideal'),
            pains=pains_text,
            desires=desires_text,
        )
        raw = self._call_openai_json(system, user_msg, temperature=0.85)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data

    # ------------------------------------------------------------------
    # MÓDULO 2.5: Maximización de Revenue (Order Bump + Upsell)
    # ------------------------------------------------------------------
    def generate_revenue_strategy(self, product_title: str,
                                  base_price: str,
                                  avatar_pain: str) -> dict:
        system = self._with_voice(REVENUE_SYSTEM_PROMPT)
        user_msg = REVENUE_USER_TEMPLATE.format(
            product_title=product_title,
            base_price=base_price,
            avatar_pain=avatar_pain,
        )
        raw = self._call_openai_json(system, user_msg, temperature=0.8)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data

    # ------------------------------------------------------------------
    # MÓDULO 3: Índice del Infoproducto
    # ------------------------------------------------------------------
    def generate_outline(self, niche_input: str, offer_data: dict) -> dict:
        system = self._with_voice(OUTLINE_SYSTEM_PROMPT)
        user_msg = OUTLINE_USER_TEMPLATE.format(
            niche=niche_input,
            product_name=offer_data.get('product_name', 'El Producto'),
            tagline=offer_data.get('tagline', ''),
        )
        raw = self._call_openai_json(system, user_msg, temperature=0.75)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data

    # ------------------------------------------------------------------
    # MÓDULO 4: Biblioteca de Copies
    # ------------------------------------------------------------------
    def generate_copy(self, niche_input: str, offer_data: dict,
                      niche_data: dict) -> dict:
        main_pain = (niche_data.get('pains', [''])[0]
                     if niche_data.get('pains') else '')
        system = self._with_voice(COPY_SYSTEM_PROMPT)
        user_msg = COPY_USER_TEMPLATE.format(
            niche=niche_input,
            product_name=offer_data.get('product_name', 'El Producto'),
            tagline=offer_data.get('tagline', ''),
            main_pain=main_pain,
        )
        raw = self._call_openai_json(system, user_msg, temperature=0.90)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data

    # ------------------------------------------------------------------
    # MODO UNIFICADO: 4 módulos en una sola llamada
    # ------------------------------------------------------------------
    def generate_all(self, niche_input: str) -> dict:
        system = self._with_voice(FULL_GENERATION_SYSTEM_PROMPT)
        user_msg = FULL_GENERATION_USER_TEMPLATE.format(niche=niche_input)
        raw = self._call_openai_json(system, user_msg, temperature=0.85)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data

    # ------------------------------------------------------------------
    # FASE 2: Escritor de Capítulos (Chaining)
    # Usa el modelo de prosa elegido (Claude o GPT-4o).
    # ------------------------------------------------------------------
    def write_chapter(self, project, chapter_data: dict,
                      previous_chapters: list,
                      user_context: str = '') -> str:
        """
        Write a single chapter as Markdown prose.

        Args:
            project: Project instance (provides title, niche_input, brand_voice)
            chapter_data: dict from ProductOutline.chapters[i]
            previous_chapters: list of already-written ChapterContent instances
                               (used to build continuity context)
            user_context: extracted text from user-uploaded PDFs / URLs
                          (injected as author knowledge base)

        Returns:
            Markdown string — the full chapter text.
        """
        voice_desc = BRAND_VOICE_PERSONAS.get(
            self.brand_voice,
            BRAND_VOICE_PERSONAS['mentor']
        )
        # Build a brief continuity summary (last 2 chapters, first 200 chars each)
        if previous_chapters:
            ctx_lines = []
            for ch in previous_chapters[-2:]:
                snippet = ch.content[:200].replace('\n', ' ')
                ctx_lines.append(
                    f"Cap. {ch.chapter_number} '{ch.title}': {snippet}..."
                )
            previous_context = '\n'.join(ctx_lines)
        else:
            previous_context = "Este es el primer capítulo — no hay capítulos previos."

        # Format user context block
        if user_context and user_context.strip():
            user_context_block = (
                f"El autor ha proporcionado las siguientes notas e investigación propia. "
                f"Usa estas ideas como base principal del capítulo:\n\n"
                f"{user_context.strip()[:8000]}"
            )
        else:
            user_context_block = (
                "No hay notas del autor para este proyecto. "
                "Usa tu conocimiento para desarrollar el tema."
            )

        key_points = chapter_data.get('key_points', [])
        key_points_str = '\n'.join(f"• {p}" for p in key_points)

        system = self._with_voice(CHAPTER_WRITER_SYSTEM_PROMPT)
        user_msg = CHAPTER_WRITER_USER_TEMPLATE.format(
            book_title=project.title or project.niche_input,
            niche_input=project.niche_input,
            brand_voice_desc=voice_desc,
            chapter_number=chapter_data.get('number', '?'),
            chapter_title=chapter_data.get('title', ''),
            chapter_description=chapter_data.get('description', ''),
            key_points=key_points_str,
            transformation=chapter_data.get('transformation', ''),
            user_context=user_context_block,
            previous_context=previous_context,
        )

        return self._call_prose(system, user_msg, temperature=0.88)

    # ------------------------------------------------------------------
    # MÓDULO 3: Avatares & Buyer Persona (AvatarProfile)
    # ------------------------------------------------------------------
    def generate_avatars(self, project) -> dict:
        """Generate 3-5 ultra-detailed buyer personas for the project."""

        offer = getattr(project, 'offer_structure', None)
        niche = getattr(project, 'niche_analysis', None)

        title = (offer.product_name if offer and offer.product_name
                 else project.title or project.niche_input)
        pains = niche.pains[:5] if niche and niche.pains else []
        desires = niche.desires[:5] if niche and niche.desires else []
        markets = project.target_markets or [project.primary_market]

        system = self._with_voice(
            "Eres un experto en psicología del consumidor digital y research de mercado para infoproductos en LATAM y España. "
            "Generas buyer personas ultra-detalladas, reales y accionables. Cada avatar tiene su propio mundo emocional, "
            "sus propias objeciones, sus propios triggers de compra y el mensaje exacto que lo hace convertir. "
            "Entrega SOLO JSON válido."
        )
        user_msg = (
            f"Producto: {title}\n"
            f"Nicho: {project.niche_input}\n"
            f"Mercados: {', '.join(markets)}\n"
            f"Dolores identificados: {pains}\n"
            f"Deseos identificados: {desires}\n\n"
            "Genera exactamente 4 buyer personas ultra-detalladas para este producto. "
            "Responde SOLO con este JSON:\n"
            '{"avatars":['
            '{"id":1,"name":"Nombre ficticio representativo","age_range":"25-35",'
            '"occupation":"Trabajo real de LATAM","location":"Ciudad, País",'
            '"income_level":"Bajo|Medio|Medio-alto",'
            '"daily_life":"Descripción de su día a día real (2-3 oraciones)",'
            '"main_pain":"Su dolor principal relacionado al producto",'
            '"secondary_pains":["dolor 2","dolor 3"],'
            '"core_desire":"Lo que más quiere lograr con el producto",'
            '"purchase_trigger":"El momento exacto en que decide comprar",'
            '"objections":["Objeción 1 literal","Objeción 2 literal"],'
            '"objection_responses":["Respuesta a objeción 1","Respuesta a objeción 2"],'
            '"hooks":["Hook emocional para feed","Hook de urgencia para stories"],'
            '"emotional_angle":"El ángulo emocional que más le mueve (miedo|esperanza|orgullo|etc)",'
            '"decision_channel":"Instagram|Facebook|TikTok|Google",'
            '"content_they_consume":"Tipo de contenido que consume",'
            '"price_sensitivity":"alta|media|baja",'
            '"buying_stage":"awareness|consideration|decision"}'
            '],'
            '"buyer_persona_summary":"Resumen ejecutivo de 3-4 oraciones del perfil común del comprador ideal"}'
        )
        raw = self._call_openai_json(system, user_msg, temperature=0.85)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data

    # ------------------------------------------------------------------
    # FÁBRICA 16: Generador genérico de artefactos por funcionalidad
    # ------------------------------------------------------------------
    def generate_factory_artifact(self, project, artifact_type: str) -> dict:
        """Generate structured artifact JSON for a pipeline feature."""

        offer = getattr(project, 'offer_structure', None)
        niche = getattr(project, 'niche_analysis', None)
        revenue = getattr(project, 'revenue_strategy', None)
        avatars_obj = getattr(project, 'avatar_profile', None)

        title = (offer.product_name if offer and offer.product_name
                 else project.title or project.niche_input)
        avatar = niche.avatar_name if niche and niche.avatar_name else 'Avatar ideal'
        pains = niche.pains[:5] if niche and niche.pains else []
        desires = niche.desires[:3] if niche and niche.desires else []
        markets = project.target_markets or [project.primary_market]
        country_hint = ', '.join(markets)
        tagline = offer.tagline if offer and offer.tagline else ''
        price = ''
        if offer and offer.price_points:
            price = str(offer.price_points[0].get('price', '')) if offer.price_points else ''
        avatars_summary = ''
        if avatars_obj and avatars_obj.avatars:
            first = avatars_obj.avatars[0]
            avatars_summary = (
                f"{first.get('name','')}: {first.get('main_pain','')} | "
                f"Trigger: {first.get('purchase_trigger','')}"
            )

        prompts = {
            'angles': {
                'task': (
                    "Genera 7 ángulos de venta distintos con alta probabilidad de conversión para este producto. "
                    "Cada ángulo debe tener: nombre memorable, hook de apertura para feed, hook alternativo para stories, "
                    "sub-ángulos (al menos 2 variaciones), la objeción que derriba, el avatar al que apunta más, "
                    "y la prioridad de testeo (high/medium/low)."
                ),
                'schema': (
                    '{"angles":['
                    '{"id":1,"name":"Nombre del ángulo","hook_feed":"Hook para feed 1-2 líneas",'
                    '"hook_stories":"Hook de stories corto",'
                    '"sub_angles":["variación A","variación B"],'
                    '"objection_destroyed":"La objeción que resuelve",'
                    '"best_avatar":"Nombre del avatar objetivo",'
                    '"emotional_driver":"miedo|esperanza|orgullo|identidad|urgencia",'
                    '"test_priority":"high|medium|low"}'
                    ']}'
                ),
            },
            'visual_identity': {
                'task': (
                    "Crea la identidad visual completa para este infoproducto como si fueras un branding studio senior. "
                    "Incluye: paleta de 5 colores HEX con nombres y usos específicos, 2 familias tipográficas (heading + body) "
                    "con justificación, tagline definitivo, tone of voice, 3 estilos de inspiración visual (p.ej. 'Apple meets Notion'), "
                    "brief para logo en texto, descripción del look & feel para aplicar en toda la marca."
                ),
                'schema': (
                    '{"brand_name":"","tagline":"","palette":['
                    '{"name":"Primary","hex":"#XXXXXX","use":"Para qué se usa"},'
                    '{"name":"Secondary","hex":"#XXXXXX","use":""},'
                    '{"name":"Accent","hex":"#XXXXXX","use":"CTAs, badges"},'
                    '{"name":"Background","hex":"#XXXXXX","use":""},'
                    '{"name":"Text","hex":"#XXXXXX","use":""}],'
                    '"fonts":[{"role":"Heading","name":"Nombre fuente","google_url":"https://fonts.google.com/...","why":"Justificación"},'
                    '{"role":"Body","name":"Nombre fuente","google_url":"","why":""}],'
                    '"tone":"Descripción del tono de voz",'
                    '"style_directions":["Referencia visual 1","Referencia 2","Referencia 3"],'
                    '"logo_brief":"Brief textual para diseñar el logo",'
                    '"look_and_feel":"Descripción del look & feel general",'
                    '"dont_list":["Qué evitar en el diseño 1","Qué evitar 2"]}'
                ),
            },
            'mockups': {
                'task': (
                    "Genera 8 prompts de mockup fotorrealistas para diferentes formatos del infoproducto: "
                    "portada ebook principal, portada de cada bonus (al menos 3), mockup 3D en contexto lifestyle, "
                    "mockup flat-lay para ads, bundle pack view, mockup para stories vertical. "
                    "Cada prompt debe ser en inglés, muy detallado, estilo Midjourney/DALL-E, listo para copiar y pegar."
                ),
                'schema': (
                    '{"provider":"Midjourney / DALL-E 3 / Stable Diffusion",'
                    '"mockup_prompts":['
                    '{"id":1,"format":"ebook_cover|bonus_cover|lifestyle_3d|flatlay|bundle|stories",'
                    '"title":"Nombre descriptivo del mockup",'
                    '"prompt":"Full English prompt ready to paste",'
                    '"dimensions":"1000x1400px | 1080x1080px | 1080x1920px",'
                    '"negative_prompt":"what to avoid"}'
                    ']}'
                ),
            },
            'ads_generator': {
                'task': (
                    "Genera 8 creativos publicitarios en formatos distintos listos para Meta Ads. "
                    "Formatos: Before/After, FAQ Visual, Us vs Them, Urgencia/Prueba Social, "
                    "Transformación (resultado), Objeción Resuelta, Testimonio Visual, Hook de Pattern Interrupt. "
                    "Para cada uno: headline principal, copy del overlay, brief visual detallado, "
                    "dimensiones, plataforma objetivo."
                ),
                'schema': (
                    '{"creatives":['
                    '{"id":1,"format":"before_after|faq_visual|us_vs_them|urgency|transformation|objection|testimonial|pattern_interrupt",'
                    '"headline":"Headline principal del creativo",'
                    '"copy_overlay":"Texto corto del overlay",'
                    '"visual_brief":"Descripción detallada del visual para el diseñador",'
                    '"dimensions":"1080x1080 | 1080x1350 | 1080x1920",'
                    '"platform":"feed|stories|reels",'
                    '"cta":"Texto del botón CTA",'
                    '"why_it_works":"Por qué este formato convierte"}'
                    ']}'
                ),
            },
            'nano_banana_ads': {
                'task': (
                    "Genera 10 prompts de imágenes publicitarias profesionales para el Generador de Imágenes ADS. "
                    "Incluye: prompts en inglés para Midjourney/DALL-E 3, orientados a alta conversión en Meta Ads, "
                    "con descripción del escenario, modelo (si aplica), producto, colores de marca y mood. "
                    "Formatos: cuadrado (feed), vertical (stories), horizontal (display)."
                ),
                'schema': (
                    '{"provider":"nano_banana_3_pro",'
                    '"estimated_seconds":60,'
                    '"assets":['
                    '{"id":1,"format":"square|story|horizontal",'
                    '"prompt":"Detailed English image generation prompt",'
                    '"mood":"Professional|Lifestyle|Emotional|Dramatic",'
                    '"cta_overlay":"Texto CTA sugerido para el overlay",'
                    '"best_for":"feed|stories|display"}'
                    ']}'
                ),
            },
            'offer_visual_model': {
                'task': (
                    "Modela visualmente la oferta completa: value stack con métricas de valor, "
                    "anclas de precio psicológico, objeciones pre-resueltas, garantía propuesta, "
                    "urgencia y escasez (si aplica), bonus stack visual, y la historia de la oferta "
                    "('de X a Y en Z tiempo'). Todo orientado a maximizar conversión en landing."
                ),
                'schema': (
                    '{"offer_headline":"Headline de la oferta",'
                    '"transformation":"De [situación actual] a [resultado deseado] en [tiempo]",'
                    '"value_stack":['
                    '{"item":"Nombre del componente","value_usd":0,"tagline":""}],'
                    '"total_value_usd":0,"your_price_usd":0,'
                    '"price_anchors":["Ancla 1","Ancla 2"],'
                    '"objections_resolved":['
                    '{"objection":"","response":""}],'
                    '"guarantee":{"type":"","days":7,"copy":""},'
                    '"urgency_copy":"","scarcity_copy":"",'
                    '"bonus_stack":[{"name":"","benefit":""}],'
                    '"cta_primary":"","cta_secondary":""}'
                ),
            },
            'landing_page': {
                'task': (
                    "Genera una landing page de alta conversión COMPLETA. Incluye: "
                    "10 secciones con headline, subheadline y copy de cada bloque "
                    "(Hero, Problema, Solución, Beneficios, Cómo funciona, Para quién es, "
                    "Value Stack, Testimonios placeholder, Garantía, CTA Final). "
                    "Además: meta title, meta description, y un snippet HTML/CSS funcional del Hero section "
                    "listo para copiar en Shopify o WordPress."
                ),
                'schema': (
                    '{"meta_title":"","meta_description":"",'
                    '"sections":['
                    '{"id":1,"name":"hero|problem|solution|benefits|how_it_works|for_who|value_stack|testimonials|guarantee|cta",'
                    '"headline":"","subheadline":"","copy":"","cta":""}],'
                    '"hero_html":"<!-- HTML snippet del hero section -->",'
                    '"color_scheme":"basado en identidad visual"}'
                ),
            },
            'product_copies': {
                'task': (
                    "Genera 5 descripciones de producto distintas para usar en tienda/landing, "
                    "cada una con un ángulo de persuasión diferente: "
                    "1) Emocional (transforma con historia), 2) Racional (argumentos y datos), "
                    "3) Urgencia/Escasez (ahora o nunca), 4) Prueba Social (como todos lo hacen), "
                    "5) Problema-Agitación-Solución (el clásico PAS). "
                    "Cada descripción: 3-5 párrafos, lista de beneficios bullet points, CTA final."
                ),
                'schema': (
                    '{"variants":['
                    '{"id":1,"style":"emocional|racional|urgencia|social_proof|PAS",'
                    '"headline":"Headline de la descripción",'
                    '"copy":"Texto completo 3-5 párrafos",'
                    '"bullets":["Beneficio concreto 1","Beneficio 2","Beneficio 3"],'
                    '"cta":"Texto del botón de compra"}'
                    ']}'
                ),
            },
            'ad_copies': {
                'task': (
                    "Genera batería completa de copys para Meta Ads de público frío. "
                    "3 copys cortos para feed (80-120 palabras, hook potente), "
                    "3 copys ultra-cortos para stories (30-50 palabras, visual + copy integrado), "
                    "2 copys largos para conversión (300-500 palabras, estructura AIDA), "
                    "5 headlines alternativos (para A/B test), "
                    "5 hooks de apertura (primeras 2 líneas). "
                    "Todo adaptado al mercado: " + country_hint
                ),
                'schema': (
                    '{"feed_copies":['
                    '{"id":1,"copy":"80-120 palabras","primary_text":"Texto principal","headline":"","cta":""}],'
                    '"stories_copies":['
                    '{"id":1,"copy":"30-50 palabras","visual_note":""}],'
                    '"long_form_copies":['
                    '{"id":1,"copy":"300-500 palabras AIDA"}],'
                    '"headline_variations":["headline 1","headline 2","headline 3","headline 4","headline 5"],'
                    '"hook_openers":["hook 1","hook 2","hook 3","hook 4","hook 5"]}'
                ),
            },
            'premium_scripts': {
                'task': (
                    "Genera 8 guiones persuasivos completos para videos de venta: "
                    "2 hooks de 15 segundos (atención inmediata), "
                    "2 guiones de 60 segundos (problema + solución + CTA), "
                    "2 guiones de 90 segundos (historia + transformación + CTA), "
                    "1 guión tipo 'Demo del producto' (muestra lo que consiguen), "
                    "1 guión tipo 'Testimonio dramatizado'. "
                    "Cada guión: texto completo, indicaciones de voz/tono, notas de cámara."
                ),
                'schema': (
                    '{"scripts":['
                    '{"id":1,"type":"hook_15s|script_60s|script_90s|demo|testimonial",'
                    '"title":"Nombre descriptivo del guión",'
                    '"duration":"15s|60s|90s",'
                    '"script":"Texto completo del guión con [PAUSA], [ÉNFASIS], etc.",'
                    '"voice_tone":"Descripción del tono de voz",'
                    '"camera_notes":"Indicaciones de cámara/edición",'
                    '"hook_line":"Primera línea del guión"}'
                    ']}'
                ),
            },
            'ugc_realistic': {
                'task': (
                    "Genera 6 prompts ultra-realistas para UGC (User Generated Content) "
                    "optimizados para Sora, VEO 3, Kling y Runway. "
                    "Para cada uno: descripción del creador UGC (edad, look, ubicación), "
                    "escenario/contexto detallado, acción que realiza, iluminación, "
                    "lo que dice o muestra del producto, y shotlist de 3-4 planos. "
                    "Mezcla: review en casa, unboxing en calle, resultado antes/después, uso cotidiano."
                ),
                'schema': (
                    '{"ugc_prompts":['
                    '{"id":1,"tool":"Sora|VEO3|Kling|Runway",'
                    '"type":"review|unboxing|result|daily_use",'
                    '"creator_profile":"Descripción del creador UGC",'
                    '"scenario":"Escenario detallado",'
                    '"prompt":"Prompt completo en inglés para la herramienta",'
                    '"shotlist":["Plano 1","Plano 2","Plano 3"],'
                    '"audio_note":"Indicación de audio o voz"}'
                    ']}'
                ),
            },
            'product_bonus_pack': {
                'task': (
                    "Genera el producto digital completo con su paquete de bonuses. "
                    "Producto principal: nombre definitivo, promesa central, tabla de contenidos (8-10 secciones), "
                    "entregables (PDF, workbook, etc.), tiempo estimado de consumo. "
                    "5 bonuses: cada uno con nombre, beneficio concreto, formato, valor percibido en USD, "
                    "y por qué complementa el producto principal. "
                    "Incluye también brief para portada de cada bonus."
                ),
                'schema': (
                    '{"main_product":{"name":"","promise":"","table_of_contents":[""],'
                    '"deliverables":["PDF","Workbook"],"consumption_time":""},'
                    '"bonuses":['
                    '{"id":1,"name":"","benefit":"","format":"PDF|Video|Checklist|Template",'
                    '"perceived_value_usd":0,"why_complementary":"","cover_brief":""}],'
                    '"total_perceived_value_usd":0}'
                ),
            },
            'email_marketing': {
                'task': (
                    "Crea 8 plantillas de email marketing completas: "
                    "2 de carrito abandonado (1h y 24h después), "
                    "3 de lanzamiento (pre-lanzamiento hype, día de apertura, último día), "
                    "2 de nurturing/onboarding (bienvenida + quick win en día 1, entrega de valor día 3), "
                    "1 de reactivación (para suscriptores fríos). "
                    "Cada email: asunto, preview text, estructura del cuerpo completo, CTA principal."
                ),
                'schema': (
                    '{"emails":['
                    '{"id":1,"type":"abandoned_1h|abandoned_24h|launch_pre|launch_open|launch_last|nurture_welcome|nurture_day3|reactivation",'
                    '"subject":"Asunto del email (con emoji)",'
                    '"preview_text":"Texto preview corto",'
                    '"body":"Cuerpo completo del email",'
                    '"cta_text":"Texto del botón CTA",'
                    '"cta_url_placeholder":"[URL]",'
                    '"send_timing":"Cuándo enviarlo"}'
                    ']}'
                ),
            },
            'global_export': {
                'task': (
                    "Genera guía práctica completa para vender este infoproducto fuera del país de origen. "
                    "8 secciones: 1) Estructura legal recomendada por país (AR/MX/CO/CL/ES), "
                    "2) Plataformas de pago internacionales (Stripe, PayPal, Hotmart, Gumroad), "
                    "3) Fiscalidad y facturación por mercado, "
                    "4) Propiedad intelectual y registro, "
                    "5) Adaptación cultural del copy (diferencias clave AR vs MX vs ES), "
                    "6) Estrategia de precios por mercado (PPP), "
                    "7) Herramientas recomendadas por mercado, "
                    "8) Checklist de lanzamiento global (10 pasos)."
                ),
                'schema': (
                    '{"sections":['
                    '{"id":1,"topic":"legal|payments|taxes|ip|copy_adaptation|pricing|tools|checklist",'
                    '"title":"Título de la sección",'
                    '"summary":"Resumen ejecutivo 2-3 oraciones",'
                    '"key_points":["Punto clave 1","Punto clave 2"],'
                    '"actions":["Acción concreta 1","Acción concreta 2"],'
                    '"markets_mentioned":["AR","MX"]}'
                    ']}'
                ),
            },
        }

        if artifact_type not in prompts:
            raise ValueError(f'Tipo de artefacto no soportado: {artifact_type}')

        config = prompts[artifact_type]
        system = self._with_voice(
            "Eres un equipo senior de Growth, Marketing, Copywriting y Product Design especializado "
            "en infoproductos digitales para LATAM y España. "
            "Tu output es concreto, accionable y listo para usar — sin relleno genérico. "
            "Entrega JSON válido siguiendo el esquema exacto indicado."
        )
        user_msg = (
            f"Producto: {title}\n"
            f"Nicho: {project.niche_input}\n"
            f"Avatar principal: {avatar}\n"
            f"Dolores clave: {pains}\n"
            f"Deseos: {desires}\n"
            f"Mercados: {country_hint}\n"
            f"Tagline: {tagline}\n"
            f"Precio base: {price or 'no definido'}\n"
            f"Avatar detallado: {avatars_summary}\n"
            f"Oferta base: {offer.product_name if offer else title}\n"
            f"Order bump: {revenue.order_bump if revenue else {}}\n"
            f"Upsell: {revenue.upsell if revenue else {}}\n\n"
            f"TAREA: {config['task']}\n\n"
            f"Responde SOLO con este esquema JSON exacto:\n{config['schema']}"
        )

        raw = self._call_openai_json(system, user_msg, temperature=0.82)
        data = self._parse_json(raw)
        data['raw_response'] = raw
        return data


