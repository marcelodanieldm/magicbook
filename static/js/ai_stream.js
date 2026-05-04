/**
 * MagicBook — AI Module Generation
 * Handles all fetch calls to the Django AI endpoints and updates the UI.
 */

const MODULE_CONFIG = {
  niche: {
    url: (id) => `/dashboard/api/generate/niche/${id}/`,
    title: 'Analizando tu nicho con IA...',
    desc: 'Detectando dolores, deseos y perfil del avatar',
    color: 'violet',
  },
  offer: {
    url: (id) => `/dashboard/api/generate/offer/${id}/`,
    title: 'Construyendo tu oferta irresistible...',
    desc: 'Calculando precio psicológico, bonuses y garantía',
    color: 'yellow',
  },
  revenue: {
    url: (id) => `/dashboard/api/generate/revenue/${id}/`,
    title: 'Diseñando tu motor de maximización de ingresos...',
    desc: 'Creando Order Bump + Upsell con lógica de AOV/LTV',
    color: 'emerald',
  },
  outline: {
    url: (id) => `/dashboard/api/generate/outline/${id}/`,
    title: 'Generando el índice de tu E-book...',
    desc: 'Estructurando 10 capítulos de alto impacto',
    color: 'blue',
  },
  copy: {
    url: (id) => `/dashboard/api/generate/copy/${id}/`,
    title: 'Escribiendo tus copies de venta...',
    desc: 'Headlines, hooks, PAS y AIDA listos para publicar',
    color: 'pink',
  },
  all: {
    url: (id) => `/dashboard/api/generate/all/${id}/`,
    title: 'El Arquitecto está construyendo tu ecosistema...',
    desc: 'Avatar · Oferta · Revenue · Índice · Copies',
    color: 'violet',
  },
};

let loadingBarTimer = null;
let loadingNarrativeTimer = null;

const NARRATIVE_LINES = {
  niche: [
    'MagicBook esta analizando los dolores de tu audiencia...',
    'Comparando patrones de deseo y objecion...',
    'Definiendo avatares accionables para vender mejor...',
  ],
  offer: [
    'MagicBook esta creando una oferta irresistible...',
    'Ajustando valor percibido, bonus y garantia...',
    'Optimizando precio para conversion inicial...',
  ],
  revenue: [
    'MagicBook esta calibrando tu motor de revenue...',
    'Diseñando order bump y upsell con logica de ticket...',
    'Preparando flujo de monetizacion por capas...',
  ],
  outline: [
    'MagicBook esta estructurando tu libro paso a paso...',
    'Ordenando capitulos por impacto y claridad...',
    'Preparando una ruta de transformacion para el lector...',
  ],
  copy: [
    'MagicBook esta puliendo tus mensajes de venta...',
    'Creando hooks, headlines y CTAs listos para publicar...',
    'Alineando tono de marca con conversion...',
  ],
  all: [
    'MagicBook esta construyendo tu ecosistema completo...',
    'Conectando nicho, oferta, libro y copies en una sola narrativa...',
    'Afinando detalles finales para lanzamiento...',
  ],
};

function getCsrfToken() {
  const el = document.querySelector('[name=csrfmiddlewaretoken]');
  if (el) return el.value;
  // Try cookie fallback
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

function showLoading(module) {
  const cfg = MODULE_CONFIG[module];
  document.getElementById('loading-title').textContent = cfg.title;
  document.getElementById('loading-desc').textContent = cfg.desc;
  document.getElementById('loading-overlay').classList.remove('hidden');
  const skeleton = document.getElementById(`skeleton-${module}`);
  if (skeleton) skeleton.classList.remove('hidden');

  const activeCard = document.getElementById(`card-${module}`);
  if (activeCard) {
    activeCard.classList.add('ai-writing-pulse');
  }

  const loadingBar = document.getElementById('magic-loading-bar');
  const loadingDesc = document.getElementById('loading-desc');
  const narrative = NARRATIVE_LINES[module] || [cfg.desc];
  let narrativeIndex = 0;

  if (loadingNarrativeTimer) {
    window.clearInterval(loadingNarrativeTimer);
  }
  if (loadingDesc) {
    loadingDesc.textContent = narrative[0];
    loadingNarrativeTimer = window.setInterval(() => {
      narrativeIndex = (narrativeIndex + 1) % narrative.length;
      loadingDesc.textContent = narrative[narrativeIndex];
    }, 1700);
  }

  if (loadingBar) {
    let width = 18;
    loadingBar.style.width = `${width}%`;
    if (loadingBarTimer) {
      window.clearInterval(loadingBarTimer);
    }
    loadingBarTimer = window.setInterval(() => {
      width = Math.min(width + (Math.random() * 9), 92);
      loadingBar.style.width = `${width}%`;
    }, 420);
  }
}

function hideLoading(module) {
  document.getElementById('loading-overlay').classList.add('hidden');
  const skeleton = document.getElementById(`skeleton-${module}`);
  if (skeleton) skeleton.classList.add('hidden');

  const activeCard = document.getElementById(`card-${module}`);
  if (activeCard) {
    activeCard.classList.remove('ai-writing-pulse');
  }

  const loadingBar = document.getElementById('magic-loading-bar');
  if (loadingBar) {
    loadingBar.style.width = '100%';
    window.setTimeout(() => {
      loadingBar.style.width = '18%';
    }, 240);
  }
  if (loadingBarTimer) {
    window.clearInterval(loadingBarTimer);
    loadingBarTimer = null;
  }
  if (loadingNarrativeTimer) {
    window.clearInterval(loadingNarrativeTimer);
    loadingNarrativeTimer = null;
  }
}

async function generateModule(module, projectId) {
  const cfg = MODULE_CONFIG[module];
  showLoading(module);

  try {
    const response = await fetch(cfg.url(projectId), {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (data.success) {
      // Reload the page to show the freshly generated content
      window.location.reload();
    } else {
      hideLoading(module);
      showError(data.error || 'Ocurrió un error. Intenta de nuevo.');
    }
  } catch (err) {
    hideLoading(module);
    showError('Error de conexión. Verifica tu API key y vuelve a intentarlo.');
  }
}

/**
 * Shortcut for the unified 'Generar Todo' CTA button.
 * Triggers the single-call Arquitecto de Infoproductos endpoint.
 */
function generateAll(projectId) {
  generateModule('all', projectId);
}

function showError(message) {
  const div = document.createElement('div');
  div.className =
    'fixed bottom-6 right-6 bg-red-900 border border-red-700 text-red-200 px-5 py-4 rounded-xl shadow-xl max-w-sm z-50 text-sm';
  div.innerHTML = `<strong>Error:</strong> ${message}`;
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 6000);
}

function toggleCopy(type) {
  const el = document.getElementById(`copy-${type}`);
  const icon = document.getElementById(`${type}-icon`);
  if (el.classList.contains('hidden')) {
    el.classList.remove('hidden');
    icon.textContent = '▲ ocultar';
  } else {
    el.classList.add('hidden');
    icon.textContent = '▼ ver';
  }
}

function copyCTA(btn) {
  const text = btn.dataset.text;
  navigator.clipboard.writeText(text).then(() => {
    const original = btn.textContent;
    btn.textContent = '✓ Copiado';
    btn.classList.add('border-green-600', 'text-green-400');
    setTimeout(() => {
      btn.textContent = original;
      btn.classList.remove('border-green-600', 'text-green-400');
    }, 1500);
  });
}
