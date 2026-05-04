# MagicBook

> **La fábrica de infoproductos con IA más completa en español.**  
> Transforma cualquier idea o nicho en un producto digital listo para vender — con copy, avatares, estructura, emails y más — en minutos.

---

## Tabla de contenidos

1. [¿Qué es MagicBook?](#qué-es-magicbook)
2. [Problemas que resuelve](#problemas-que-resuelve)
3. [La Fábrica de 16 pasos](#la-fábrica-de-16-pasos)
4. [Planes y precios](#planes-y-precios)
5. [Flow del usuario — Plan A](#flow-del-usuario--plan-a)
6. [Stack tecnológico](#stack-tecnológico)
7. [Estructura del proyecto](#estructura-del-proyecto)
8. [Configuración del entorno](#configuración-del-entorno)
9. [Instalación y arranque local](#instalación-y-arranque-local)
10. [Comandos útiles](#comandos-útiles)

---

## ¿Qué es MagicBook?

MagicBook es una plataforma web SaaS construida con Django que permite a emprendedores, creadores de contenido y marketers **crear y lanzar infoproductos digitales (e-books, mini cursos, guías, etc.) completamente asistidos por IA**.

El usuario ingresa un nicho o una idea en lenguaje natural — por ejemplo *"quiero vender un curso de finanzas personales para jóvenes de 20 a 30 años"* — y MagicBook orquesta una serie de llamadas estructuradas a GPT-4o y/o Claude 3.5 Sonnet para producir todos los activos necesarios: análisis de avatar, oferta, índice del producto, copies de venta, guiones para ads, landing page, emails y más.

---

## Problemas que resuelve

| Problema del emprendedor | Solución MagicBook |
|---|---|
| No sabe cómo validar si su nicho tiene demanda real | Análisis de avatar profundo con dolores, deseos y barreras de compra generado por IA |
| Tarda semanas en construir una oferta coherente | Modelado de oferta con precio psicológico, bonuses con valor percibido y garantía generado en segundos |
| No sabe escribir copy ni contratar copywriters | Copies listos para producto y para ads (PAS, AIDA, hooks para Meta/TikTok) |
| No puede pagar una agencia de branding | Identidad visual, mockups y guiones UGC generados automáticamente |
| Lanza en un solo mercado y pierde escala | Multi-mercado nativo: AR, MX, CO, CL, UY, BR, ES y más |
| Tiene que usar 10 herramientas distintas | Todo el workflow en una sola plataforma, en español |

---

## La Fábrica de 16 pasos

La **Fábrica de Infoproductos** es el corazón de MagicBook. Cada proyecto atraviesa un pipeline de 16 módulos que se ejecutan de forma independiente y pueden regenerarse individualmente en cualquier momento.

| # | Paso | Descripción | Tipo |
|---|---|---|---|
| 1 | **Modelado de Oferta** | Estructura completa de la oferta: precio psicológico, value stack, garantía, bonuses con valor percibido | Nativo |
| 2 | **Investigación de Mercado** | Análisis de demanda, competencia, tendencias y oportunidades del nicho en el mercado objetivo | Nativo |
| 3 | **Avatares & Buyer Persona** | Perfiles psicológicos detallados con nombre, historia, dolores, deseos y objeciones | Nativo |
| 4 | **Generador de Ángulos** | 10+ ángulos de mensaje únicos para diferenciar la oferta y testear creatividades | Artefacto IA |
| 5 | **Identidad Visual** | Brief de branding: paleta de colores, tipografías, estilo y mood board para el producto | Artefacto IA |
| 6 | **Mockups Premium** | Descripción detallada de mockups fotorrealistas del producto digital para usar en ads | Artefacto IA |
| 7 | **Generador de Ads** | Creatividades completas para Meta Ads y TikTok Ads listas para producir | Artefacto IA |
| 8 | **Landing Page** | Estructura completa de la landing page con headline, subhead, secciones, CTA y prueba social | Artefacto IA |
| 9 | **Copys de Producto** | Copy completo del producto: sales letter, bullets de beneficios, manejo de objeciones | Artefacto IA |
| 10 | **Copys para Ads** | Textos publicitarios en formato PAS y AIDA para diferentes formatos de ad | Artefacto IA |
| 11 | **Guiones Premium** | Guiones de video para VSL, reels y stories con estructura narrativa de alta conversión | Artefacto IA |
| 12 | **UGC Realistas** | Guiones de User Generated Content con briefings de perfil, contexto y puntos de dolor | Artefacto IA |
| 13 | **Generador de Producto** | Índice del e-book con 10 capítulos + estructura de cada uno, listo para escribir | Nativo |
| 14 | **Upsells + AOV** | Estrategia de upsell, order bump y flujo post-compra para maximizar el ticket promedio | Nativo |
| 15 | **Email Marketing** | Secuencia completa de emails de bienvenida, nutrición y venta para el producto | Artefacto IA |
| 16 | **Exportar y Vender Global** | Estrategia de internacionalización, plataformas y checklist de lanzamiento multi-mercado | Artefacto IA |

> **Escritor de capítulos (Fase 2):** Una vez generado el índice, MagicBook puede escribir cada capítulo del e-book completo con el tono de marca elegido, capitulo a capitulo o todos en secuencia mediante Server-Sent Events (SSE).

---

## Planes y precios

### Plan A — $29 USD / único pago

El plan de entrada que activa el acceso completo a la plataforma.

- +20 testeos de producto en simultáneo
- Los 16 pasos del workflow completo
- Generación ilimitada por testeo
- Investigación de mercado profunda automatizada
- Generador de Landing Page en 60 segundos
- Generador de guiones y UGC que venden
- Generación de copys listos para usar
- Generación de imágenes ADS con NANO BANANA 3 PRO
- Generador de producto y bonus dentro de la app
- Multi-mercado: AR, MX, CO, CL, UY, BR, ES + más
- Modelado de oferta con IA visual
- Logo + identidad visual con IA generativa

---

## Flow del usuario — Plan A

```
1. Registro
   └─ El usuario completa el formulario con username, email y contraseña.
   └─ Se crea la cuenta y se activa automáticamente el Plan A.
   └─ Se envía email transaccional con credenciales y links de acceso.

2. Onboarding (3 pasos)
   ├─ Paso 1: Credenciales enviadas ✅
   ├─ Paso 2: Primer login detectado ✅
   └─ Paso 3: Primer proyecto lanzado ✅

3. Dashboard
   └─ Vista de todos los proyectos activos con estado de completitud.

4. Crear Proyecto
   ├─ Ingresa el nicho o idea en texto libre.
   ├─ Elige la Voz de Marca: Mentor / Amigo / Científico / Coach / Experto.
   ├─ Elige el Modelo de IA: GPT-4o (estructurado) o Claude 3.5 Sonnet (creativo).
   └─ Selecciona el mercado principal y mercados objetivo adicionales.

5. Pipeline de generación clásica (4 módulos base)
   ├─ Análisis de Nicho      → avatar, dolores, deseos, miedos, barreras
   ├─ Oferta Irresistible    → precio, bonuses, garantía, value stack
   ├─ Revenue Strategy       → modelo de ingresos, upsells, proyección
   └─ Índice del E-book      → 10 capítulos estructurados con descripción

6. Fábrica de 16 pasos
   └─ Accesible desde /project/<id>/factory/
   └─ Cada módulo se genera de forma independiente.
   └─ Artefactos guardados en DB, regenerables en cualquier momento.

7. Escritor de capítulos
   └─ Escribe cada capítulo completo (900-1.200 palabras) con streaming SSE.
   └─ Opción de escribir todos los capítulos en secuencia automática.

8. Descarga
   └─ E-book completo exportable como Markdown (.md).
```

---

## Stack tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Backend framework | Django | 4.2.13 |
| Lenguaje | Python | 3.11+ |
| Base de datos | SQLite (dev) / PostgreSQL (prod) | — |
| IA — JSON estructurado | OpenAI GPT-4o | API v1 |
| IA — Redacción creativa | Anthropic Claude 3.5 Sonnet | API v0 (opcional) |
| Archivos estáticos | WhiteNoise | 6.6.0 |
| Variables de entorno | python-dotenv | 1.0.1 |
| Cliente HTTP | openai SDK | 1.30.1 |
| CSS / UI | Tailwind CSS (CDN) | 3.x |
| Fuentes | Google Fonts — Inter | — |
| Streaming | Server-Sent Events (SSE) nativo Django | — |

### Dependencias opcionales

| Paquete | Para qué |
|---|---|
| `anthropic` | Activar Claude 3.5 Sonnet como modelo de escritura |
| `pypdf` | Extraer texto de PDFs para el knowledge base del escritor |
| `requests` + `beautifulsoup4` | Extraer contenido de URLs para el knowledge base |

---

## Estructura del proyecto

```
magicbook/                    ← raíz del repositorio
├── apps/
│   ├── accounts/             ← autenticación, onboarding, planes
│   │   ├── forms.py          ← formulario de registro
│   │   ├── views.py          ← login, register, plan A flow, logout
│   │   └── urls.py           ← rutas de cuentas
│   └── core/
│       ├── models.py         ← Project, NicheAnalysis, OfferStructure,
│       │                        RevenueStrategy, ProductOutline, CopyLibrary,
│       │                        ChapterContent, UserResource, ProjectArtifact,
│       │                        TestRun, PlanAEnrollment, PlanBEnrollment,
│       │                        AvatarProfile
│       ├── views.py          ← Dashboard, factory APIs, generation views, SSE
│       ├── urls.py           ← todas las rutas de la app principal
│       ├── forms.py          ← ProjectCreateForm
│       ├── admin.py          ← registro de modelos en el panel admin
│       ├── migrations/       ← historial de migraciones (0001 → 0009)
│       ├── services/
│       │   ├── ai_service.py         ← orquestador de llamadas a OpenAI / Claude
│       │   ├── prompts.py            ← todos los system prompts y user templates
│       │   └── resource_extractor.py ← extracción de PDF y URLs (knowledge base)
│       └── templatetags/
│           └── core_extras.py        ← filtro dict_get para templates
├── magicbook/
│   ├── settings.py           ← configuración Django
│   ├── urls.py               ← URLconf raíz
│   └── wsgi.py               ← entrypoint WSGI
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── accounts/             ← login, register, plan_a_onboarding
│   └── core/                 ← dashboard, project_detail, project_factory, etc.
├── static/                   ← CSS, JS, imágenes propias
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Configuración del entorno

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/magicbook.git
cd magicbook
```

### 2. Crear el entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt

# Opcionales (recomendadas para producción completa)
pip install anthropic pypdf requests beautifulsoup4
```

### 4. Crear el archivo `.env`

Copia el ejemplo y completa los valores reales:

```bash
cp .env.example .env
```

Variables disponibles en `.env`:

```dotenv
# Seguridad Django
SECRET_KEY=genera-una-clave-segura-con-django-secret-key-gen
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI (obligatorio)
OPENAI_API_KEY=sk-...tu-api-key

# Modelo de IA por defecto
AI_MODEL=gpt-4o

# Anthropic Claude (opcional — solo si quieres el modelo creativo)
ANTHROPIC_API_KEY=sk-ant-...

# Email — desarrollo (imprime emails en consola)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=MagicBook <no-reply@magicbook.local>

# Email — producción SMTP (ejemplo SendGrid)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_PORT=587
# EMAIL_HOST_USER=apikey
# EMAIL_HOST_PASSWORD=SG.xxxxxxxx
# EMAIL_USE_TLS=True
```

### 5. Aplicar migraciones y crear superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

La app queda disponible en [http://localhost:8000](http://localhost:8000).  
El panel de administración en [http://localhost:8000/admin/](http://localhost:8000/admin/).

---

## Comandos útiles

```bash
# Verificar que el proyecto no tiene errores de configuración
python manage.py check

# Crear migraciones tras cambios en modelos
python manage.py makemigrations

# Aplicar migraciones pendientes
python manage.py migrate

# Recopilar archivos estáticos (producción)
python manage.py collectstatic --noinput

# Abrir shell interactivo de Django
python manage.py shell
```

---

## Variables de modelos de IA

| Valor `AI_MODEL` | Uso recomendado |
|---|---|
| `gpt-4o` | JSON estructurado — todos los módulos de análisis y oferta |
| `claude-3-5-sonnet-20241022` | Redacción creativa — capítulos del e-book |

> Los módulos de la Fábrica 16 **siempre usan GPT-4o** para garantizar salida JSON válida, independientemente del modelo elegido por el usuario. El modelo seleccionado por el usuario solo afecta al Escritor de Capítulos.

---

## Voces de marca disponibles

| Clave | Descripción |
|---|---|
| `mentor` | 🎓 Mentor Sabio y Empático — cálido, con analogías de vida real |
| `friend` | 😎 Amigo Sarcástico y Directo — humor, va al grano |
| `scientist` | 🔬 Científico Riguroso — datos, evidencia, terminología precisa |
| `coach` | 💪 Coach Motivacional — energía, urgencia, frases cortas |
| `expert` | 🏆 Experto Autoritario — credibilidad máxima, casos de estudio |

---

## Licencia

Propietario — todos los derechos reservados. © 2026 MagicBook.
