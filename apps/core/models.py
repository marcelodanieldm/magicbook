"""Domain models for the MagicBook product generation workflow."""

from django.db import models
from django.contrib.auth.models import User


# Shared selection catalogs used across forms and AI configuration.
BRAND_VOICE_CHOICES = [
    ('mentor',    '🎓 Mentor Sabio y Empático'),
    ('friend',    '😎 Amigo Sarcástico y Directo'),
    ('scientist', '🔬 Científico Riguroso y Preciso'),
    ('coach',     '💪 Coach Motivacional Intenso'),
    ('expert',    '🏆 Experto Autoritario y Serio'),
]

AI_MODEL_CHOICES = [
    ('gpt-4o',                       'GPT-4o — Estructura y JSON'),
    ('claude-3-5-sonnet-20241022',   'Claude 3.5 Sonnet — Redacción Creativa'),
]

MARKET_CHOICES = [
    ('AR', 'Argentina'),
    ('MX', 'México'),
    ('CO', 'Colombia'),
    ('CL', 'Chile'),
    ('UY', 'Uruguay'),
    ('BR', 'Brasil'),
    ('ES', 'España'),
    ('OTRO', 'Otro mercado'),
]


# Main project container: user input, generation configuration and state.
class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('niche_done', 'Nicho Analizado'),
        ('offer_done', 'Oferta Creada'),
        ('revenue_done', 'Revenue Diseñado'),
        ('outline_done', 'Índice Creado'),
        ('copy_done', 'Copies Generados'),
        ('complete', 'Completo'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    niche_input = models.TextField(verbose_name='Nicho / Idea')
    title       = models.CharField(max_length=200, blank=True, verbose_name='Título del Proyecto')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    brand_voice = models.CharField(
        max_length=20, choices=BRAND_VOICE_CHOICES, default='mentor',
        verbose_name='Voz de Marca'
    )
    ai_model    = models.CharField(
        max_length=50, choices=AI_MODEL_CHOICES, default='gpt-4o',
        verbose_name='Modelo de IA'
    )
    primary_market = models.CharField(
        max_length=10, choices=MARKET_CHOICES, default='AR',
        verbose_name='Mercado principal'
    )
    target_markets = models.JSONField(default=list, blank=True)
    plan_tier = models.CharField(max_length=30, default='plan_a_29')
    max_simultaneous_tests = models.PositiveSmallIntegerField(default=20)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return self.title or self.niche_input[:60]

    @property
    def steps_completed(self):
        count = 0
        if hasattr(self, 'niche_analysis'):
            count += 1
        if hasattr(self, 'offer_structure'):
            count += 1
        if hasattr(self, 'revenue_strategy'):
            count += 1
        if hasattr(self, 'product_outline'):
            count += 1
        if hasattr(self, 'copy_library'):
            count += 1
        return count

    @property
    def completion_percentage(self):
        return int((self.steps_completed / 5) * 100)


class NicheAnalysis(models.Model):
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='niche_analysis'
    )
    avatar_name = models.CharField(max_length=150, blank=True)
    buyer_personas = models.JSONField(default=list)
    pains = models.JSONField(default=list)
    desires = models.JSONField(default=list)
    fears = models.JSONField(default=list)
    barriers = models.JSONField(default=list)
    product_names = models.JSONField(default=list)
    epiphany_bridge = models.TextField(blank=True)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Análisis de Nicho'

    def __str__(self):
        return f"Nicho: {self.project}"


class OfferStructure(models.Model):
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='offer_structure'
    )
    product_name = models.CharField(max_length=200, blank=True)
    tagline = models.CharField(max_length=350, blank=True)
    price_points = models.JSONField(default=list)
    bonuses = models.JSONField(default=list)
    guarantee = models.TextField(blank=True)
    value_stack = models.JSONField(default=list)
    total_value = models.CharField(max_length=50, blank=True)
    your_investment = models.CharField(max_length=50, blank=True)
    upsell = models.JSONField(default=dict)
    order_bump = models.JSONField(default=dict)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Estructura de Oferta'

    def __str__(self):
        return f"Oferta: {self.product_name}"


class ProductOutline(models.Model):
    PRODUCT_TYPES = [
        ('ebook', 'E-book'),
        ('course', 'Curso'),
        ('workbook', 'Workbook'),
        ('guide', 'Guía Rápida'),
    ]

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='product_outline'
    )
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='ebook')
    title = models.CharField(max_length=250, blank=True)
    subtitle = models.CharField(max_length=350, blank=True)
    description = models.TextField(blank=True)
    chapters = models.JSONField(default=list)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Índice del Producto'

    def __str__(self):
        return f"Índice: {self.title}"


class CopyLibrary(models.Model):
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='copy_library'
    )
    headlines = models.JSONField(default=list)
    hooks = models.JSONField(default=list)
    short_description = models.TextField(blank=True)
    pas_copy = models.TextField(blank=True)
    aida_copy = models.TextField(blank=True)
    cta_options = models.JSONField(default=list)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Biblioteca de Copies'

    def __str__(self):
        return f"Copies: {self.project}"


class AvatarProfile(models.Model):
    """Stores 3-5 ultra-detailed buyer personas generated by IA for a project."""

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='avatar_profile'
    )
    avatars = models.JSONField(default=list)
    buyer_persona_summary = models.TextField(blank=True)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Avatares y Buyer Persona'

    def __str__(self):
        return f"Avatares: {self.project}"


class RevenueStrategy(models.Model):
    """Stores AOV/LTV micro-offers: order bump and one-time upsell."""

    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name='revenue_strategy'
    )
    order_bump = models.JSONField(default=dict)
    upsell = models.JSONField(default=dict)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Estrategia de Revenue'

    def __str__(self):
        return f"Revenue: {self.project}"


class ChapterContent(models.Model):
    """Stores the full written text of each chapter (Phase 2 chaining)."""

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('done',    'Completado'),
    ]

    project        = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='chapter_contents'
    )
    chapter_number = models.PositiveSmallIntegerField()
    title          = models.CharField(max_length=250, blank=True)
    content        = models.TextField(blank=True)
    word_count     = models.PositiveIntegerField(default=0)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering       = ['chapter_number']
        unique_together = [['project', 'chapter_number']]
        verbose_name   = 'Contenido de Capítulo'

    def __str__(self):
        return f"Cap. {self.chapter_number}: {self.title}"


class UserResource(models.Model):
    """
    Stores user-provided knowledge sources (PDF files or web URLs).
    The extracted text is injected into the Chapter Writer prompt so the
    AI writes based on the author's own ideas and research, not just
    generic training data.
    """

    TYPE_CHOICES = [
        ('pdf', 'Archivo PDF'),
        ('url', 'Página Web'),
    ]

    project        = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='user_resources'
    )
    resource_type  = models.CharField(max_length=5, choices=TYPE_CHOICES)
    title          = models.CharField(max_length=300, blank=True,
                                      verbose_name='Título / descripción')
    url            = models.URLField(max_length=2000, blank=True,
                                     verbose_name='URL de la página')
    pdf_file       = models.FileField(
        upload_to='user_resources/', blank=True,
        verbose_name='Archivo PDF'
    )
    extracted_text = models.TextField(
        blank=True,
        verbose_name='Texto extraído'
    )
    char_count     = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering     = ['-created_at']
        verbose_name = 'Recurso del Usuario'

    def __str__(self):
        label = self.title or self.url or str(self.pdf_file)
        return f"[{self.resource_type.upper()}] {label[:60]}"


class ProjectArtifact(models.Model):
    """Generic storage for generated assets across the 15-feature factory."""

    TYPE_CHOICES = [
        ('angles', 'Generador de Ángulos'),
        ('visual_identity', 'Identidad Visual'),
        ('mockups', 'Mockups Premium'),
        ('ads_generator', 'Generador de Ads'),
        ('nano_banana_ads', 'Imágenes Ads NANO BANANA 3 PRO'),
        ('offer_visual_model', 'Modelado de Oferta Visual'),
        ('landing_page', 'Landing Page'),
        ('product_copies', 'Copys de Producto'),
        ('ad_copies', 'Copys para Ads'),
        ('product_bonus_pack', 'Generador de Producto + Bonus'),
        ('premium_scripts', 'Guiones Premium'),
        ('ugc_realistic', 'UGC Realistas'),
        ('email_marketing', 'Email Marketing'),
        ('global_export', 'Exportar y Vender Global'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('done', 'Completado'),
        ('error', 'Error'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='artifacts'
    )
    artifact_type = models.CharField(max_length=40, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    payload = models.JSONField(default=dict)
    raw_response = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['project', 'artifact_type']]
        ordering = ['artifact_type']
        verbose_name = 'Artefacto del Proyecto'

    def __str__(self):
        return f"{self.project_id}:{self.artifact_type}"


class TestRun(models.Model):
    """Tracks orchestrated Plan A test executions per project."""

    STATUS_CHOICES = [
        ('running', 'En ejecución'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='test_runs')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='running')
    requested_features = models.JSONField(default=list, blank=True)
    generated_count = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Ejecución de Testeo'

    def __str__(self):
        return f"TestRun #{self.pk} ({self.status})"


class PlanAEnrollment(models.Model):
    """Tracks Plan A purchase activation and onboarding milestones per user."""

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('active', 'Activo'),
        ('cancelled', 'Cancelado'),
        ('upgraded', 'Actualizado a Plan B'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='plan_a_enrollment')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    purchased_at = models.DateTimeField(null=True, blank=True)
    credentials_email_sent_at = models.DateTimeField(null=True, blank=True)
    first_login_at = models.DateTimeField(null=True, blank=True)
    first_project_launched_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True, default='')
    upgraded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan A Enrollment'

    def __str__(self):
        return f"PlanA:{self.user.username}:{self.status}"


class PlanBEnrollment(models.Model):
    """Tracks Plan B upgrade state per user (upgraded from Plan A or direct purchase)."""

    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('cancelled', 'Cancelado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='plan_b_enrollment')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    upgraded_from_plan_a = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan B Enrollment'

    def __str__(self):
        return f"PlanB:{self.user.username}:{self.status}"
