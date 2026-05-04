/**
 * MagicBook — UI Translation Dictionary
 * Supports: es (Spanish / default), en (English), pt (Portuguese / Brazil)
 *
 * Usage (after base.html sets window.UI_LANG):
 *   t('key')           → translated string
 *   t('key', {n: 5})   → translated string with {n} replaced by 5
 *   applyI18n()        → swap all [data-i18n] elements on the page
 */

(function () {
  'use strict';

  const TRANSLATIONS = {

    // ── SPANISH (default) ───────────────────────────────────────
    es: {
      // Navbar
      'nav.account':     'Mi Cuenta',
      'nav.new_project': '+ Nuevo Proyecto',
      'nav.login':       'Iniciar Sesión',
      'nav.register':    'Empezar Gratis',
      'nav.logout':      'Salir',

      // Sidebar
      'sidebar.title':    'Mapa de la Ruta',
      'sidebar.subtitle': 'El sidebar se ilumina a medida que completas cada módulo.',

      // Missions
      'mission.1.title': 'Misión 1: La Fundación',
      'mission.1.desc':  'Validar si tu idea hará dinero antes de escribir una sola palabra.',
      'mission.2.title': 'Misión 2: El Escaparate',
      'mission.2.desc':  'Tu idea empieza a verse como una empresa real.',
      'mission.3.title': 'Misión 3: Maquinaria de Ventas',
      'mission.3.desc':  'Preparamos el discurso para convencer a los desconocidos.',
      'mission.4.title': 'Misión 4: Fábrica y Escala',
      'mission.4.desc':  'Producto final y crecimiento global.',

      // Common UI
      'ui.what_for':           '¿Para qué sirve esto?',
      'ui.done':               '✓ Listo',
      'ui.next_step':          'Siguiente Paso',
      'ui.save':               '💾 Guardar',
      'ui.saved':              '✓ Guardado',
      'ui.generate':           'Generar con IA',
      'ui.regenerate':         '↻ Regenerar',
      'ui.complete_to_advance':'Completa y guarda para avanzar',
      'ui.route_complete':     'Ruta principal completada',
      'ui.completed_pill':     'Completado',
      'ui.processing_pill':    'Procesando',
      'ui.pending_pill':       'Pendiente',
      'ui.download_ebook':     '⬇️ Descargar',

      // Reference panel
      'ref.title':    'Referencia',
      'ref.subtitle': 'Resumen del paso anterior para no perder contexto.',

      // Card titles & subtitles
      'card.niche.title':   'Análisis de Nicho',
      'card.niche.sub':     'Avatar + Dolores + Deseos',
      'card.niche.hint':    'Si intentas venderle a todo el mundo, no le vendes a nadie. Aquí definiremos a quién le duele más tu solución.',
      'card.offer.title':   'Oferta Irresistible',
      'card.offer.sub':     'Precio · Bonuses · Garantía',
      'card.offer.hint':    'Ahora, convertimos el insight en una oferta irresistible.',
      'card.revenue.title': 'Revenue Management',
      'card.revenue.sub':   'Order Bump · Upsell · OTO',
      'card.revenue.hint':  'Optimiza ticket promedio antes de escalar tráfico.',
      'card.outline.title': 'Índice del Infoproducto',
      'card.outline.sub':   'E-book · 10 capítulos',
      'card.outline.hint':  'Con la oferta validada, armamos la estructura del libro.',
      'card.copy.title':    'Biblioteca de Copies',
      'card.copy.sub':      'Headlines · Hooks · Emails',
      'card.copy.hint':     'Con el índice listo, ahora creamos los textos de venta.',

      // Book editor (Step 12)
      'book.title':          'El Infoproducto',
      'book.sub':            'Editor Profesional · 15,000 – 25,000 palabras',
      'book.what_for':       'El generador masivo. Aquí la IA redacta las 40–80 páginas de tu libro o curso. Escribe capítulo a capítulo o activa el Modo Fábrica para escribirlo todo de una vez.',
      'book.progress_label': 'Progreso del manuscrito',
      'book.word_goal':      '0 / 15,000 palabras',
      'book.word_min':       'Meta mínima: 15,000',
      'book.index_title':    'Índice',
      'book.select_chapter': 'Selecciona un capítulo →',
      'book.write_btn':      '⚡ Escribir con IA',
      'book.writing':        '⚡ Escribiendo…',
      'book.save_btn':       '💾 Guardar',
      'book.reviewed':       'Revisado ✓',
      'book.expand':         '✨ Expandir Sección',
      'book.tone':           '✍️ Cambiar Tono',
      'book.example':        '💡 Añadir Ejemplo',
      'book.factory_title':  '🏭 Modo Fábrica',
      'book.factory_btn':    '⚡ Escribir Todo',
      'book.placeholder':    'Selecciona un capítulo del índice izquierdo para empezar a escribir…',
      'book.toolbar_hint':   'Selecciona texto en el editor y haz clic en',
      'book.toolbar_cta':    'Herramientas IA',
      'book.total_words':    '{n} palabras',

      // Chapter states
      'ch.pending':  'Pendiente',
      'ch.writing':  'Escribiendo…',
      'ch.done':     'Listo ✓',
      'ch.reviewed': 'Revisado ✓',

      // Length validator
      'val.short_title':  'Capítulo muy corto para marcar como revisado',
      'val.short_detail': 'Un capítulo necesita mínimo 800 palabras. Este tiene {wc}.',

      // Step names (16)
      'step.1':  'Modelado de Oferta',
      'step.2':  'Investigación',
      'step.3':  'Avatares',
      'step.4':  'Ángulos de Venta',
      'step.5':  'Identidad Visual',
      'step.6':  'Mockups Premium',
      'step.7':  'Generador de Ads',
      'step.8':  'Landing Page',
      'step.9':  'Copys de Producto',
      'step.10': 'Guiones de Video',
      'step.11': 'Prompts UGC',
      'step.12': 'Infoproducto',
      'step.13': 'Upsells + AOV',
      'step.14': 'Email Marketing',
      'step.15': 'Exportación',
      'step.16': 'Campus VIP',

      // Manual de Vuelo — hover tooltips for 16 steps
      'manual.1':  'La IA analiza el mercado real para encontrar qué vacíos dejaron tus competidores. Si intentas venderle a todos, no le vendes a nadie.',
      'manual.2':  'Define la "Gran Promesa". El "qué" vas a vender y por qué es irresistible. No se trata de vender barato, sino de volver la compra obvia.',
      'manual.3':  'Creamos perfiles psicológicos de tus compradores ideales. Dejas de venderle a "todos" para venderle a "alguien" con nombre, dolor y deseo concreto.',
      'manual.4':  'Definimos el enfoque correcto: miedo, placer o ahorro de tiempo. El ángulo perfecto para atacar la mente del comprador y duplicar la conversión.',
      'manual.5':  'Generamos tus colores y tipografías para que tu marca se vea de $10,000 USD desde el primer día.',
      'manual.6':  'Creamos imágenes 3D fotorrealistas de tu producto. Lo que entra por los ojos, se vende.',
      'manual.7':  'Diseñamos los anuncios (imágenes) que detendrán el scroll en Facebook e Instagram.',
      'manual.8':  'Construimos tu "vendedor 24/7". Tu sitio web optimizado para convertir visitas en dinero.',
      'manual.9':  'La descripción técnica y emocional que irá en tu botón de pago. Los textos que transforman atención en ventas.',
      'manual.10': 'Qué decir en tus Reels o VSL para que la gente confíe en ti y te compre.',
      'manual.11': 'Instrucciones para que creadores de contenido hablen de tu producto de forma natural y auténtica.',
      'manual.12': 'El generador masivo. Aquí la IA redacta las 40–80 páginas de tu libro o curso. Editor profesional con herramientas IA integradas.',
      'manual.13': 'Diseñamos el "combo". ¿Quieres papas con tu hamburguesa? Aumentamos tu ticket promedio con upsells estratégicos.',
      'manual.14': 'Secuencias de correos para recuperar carritos, fidelizar clientes y reactivar leads dormidos.',
      'manual.15': 'Guía paso a paso para vender fuera de tu país y cobrar en dólares o euros.',
      'manual.16': 'Tu acceso a la estrategia avanzada para escalar de tus primeros $100 a $10,000.',

      // Multi-market form
      'market.section_title': '🌎 Configuración Multi-mercado',
      'market.section_desc':  'Elige entre mercados lingüísticos (Hispano, Anglo, Luso), regiones (LATAM, USA, Europa) o países específicos (MX, AR, BR, ES…).',
      'market.primary_label': 'Mercado principal',
      'market.target_label':  'Mercados objetivo',
      // Market choice labels
      'market.HISPANO': '🌎 Hispano-parlante',
      'market.ANGLO':   '🇬🇧 Anglo-parlante',
      'market.LUSO':    '🇧🇷 Luso-parlante',
      'market.LATAM':   '🌎 Latinoamérica',
      'market.USA':     '🇺🇸 EE.UU. / USA',
      'market.EURO':    '🇪🇺 Europa',
      'market.MX':      '🇲🇽 México',
      'market.AR':      '🇦🇷 Argentina',
      'market.CO':      '🇨🇴 Colombia',
      'market.CL':      '🇨🇱 Chile',
      'market.UY':      '🇺🇾 Uruguay',
      'market.BR':      '🇧🇷 Brasil',
      'market.ES':      '🇪🇸 España',
      // Create project form
      'create.submit_btn': 'Construir mi negocio con IA →',
      'create.hint':       'Plan A USD29/mes: workflow completo + multi-mercado + testeos escalables',
    },

    // ── ENGLISH ────────────────────────────────────────────────
    en: {
      // Navbar
      'nav.account':     'My Account',
      'nav.new_project': '+ New Project',
      'nav.login':       'Sign In',
      'nav.register':    'Start Free',
      'nav.logout':      'Log Out',

      // Sidebar
      'sidebar.title':    'Route Map',
      'sidebar.subtitle': 'The sidebar lights up as you complete each module.',

      // Missions
      'mission.1.title': 'Mission 1: The Foundation',
      'mission.1.desc':  'Validate if your idea will make money before writing a single word.',
      'mission.2.title': 'Mission 2: The Showcase',
      'mission.2.desc':  'Your idea starts looking like a real business.',
      'mission.3.title': 'Mission 3: Sales Machine',
      'mission.3.desc':  'We prepare the pitch to convince strangers.',
      'mission.4.title': 'Mission 4: Factory & Scale',
      'mission.4.desc':  'Final product and global growth.',

      // Common UI
      'ui.what_for':           'What is this for?',
      'ui.done':               '✓ Done',
      'ui.next_step':          'Next Step',
      'ui.save':               '💾 Save',
      'ui.saved':              '✓ Saved',
      'ui.generate':           'Generate with AI',
      'ui.regenerate':         '↻ Regenerate',
      'ui.complete_to_advance':'Complete & save to advance',
      'ui.route_complete':     'Main route completed',
      'ui.completed_pill':     'Completed',
      'ui.processing_pill':    'Processing',
      'ui.pending_pill':       'Pending',
      'ui.download_ebook':     '⬇️ Download',

      // Reference panel
      'ref.title':    'Reference',
      'ref.subtitle': 'Summary of the previous step to keep context.',

      // Card titles & subtitles
      'card.niche.title':   'Niche Analysis',
      'card.niche.sub':     'Avatar + Pains + Desires',
      'card.niche.hint':    'If you try to sell to everyone, you sell to no one. Here we\'ll define exactly who feels your solution the most.',
      'card.offer.title':   'Irresistible Offer',
      'card.offer.sub':     'Price · Bonuses · Guarantee',
      'card.offer.hint':    'Now we turn insight into an irresistible offer.',
      'card.revenue.title': 'Revenue Management',
      'card.revenue.sub':   'Order Bump · Upsell · OTO',
      'card.revenue.hint':  'Optimize average ticket before scaling traffic.',
      'card.outline.title': 'Product Index',
      'card.outline.sub':   'E-book · 10 chapters',
      'card.outline.hint':  'With the validated offer, we structure the book.',
      'card.copy.title':    'Copy Library',
      'card.copy.sub':      'Headlines · Hooks · Emails',
      'card.copy.hint':     'With the index ready, we create the sales copy.',

      // Book editor (Step 12)
      'book.title':          'The Infoproduct',
      'book.sub':            'Professional Editor · 15,000 – 25,000 words',
      'book.what_for':       'The mass generator. AI writes your 40–80 page book or course here. Write chapter by chapter or activate Factory Mode to write everything at once.',
      'book.progress_label': 'Manuscript progress',
      'book.word_goal':      '0 / 15,000 words',
      'book.word_min':       'Minimum goal: 15,000',
      'book.index_title':    'Index',
      'book.select_chapter': 'Select a chapter →',
      'book.write_btn':      '⚡ Write with AI',
      'book.writing':        '⚡ Writing…',
      'book.save_btn':       '💾 Save',
      'book.reviewed':       'Reviewed ✓',
      'book.expand':         '✨ Expand Section',
      'book.tone':           '✍️ Change Tone',
      'book.example':        '💡 Add Example',
      'book.factory_title':  '🏭 Factory Mode',
      'book.factory_btn':    '⚡ Write All',
      'book.placeholder':    'Select a chapter from the left index to start writing…',
      'book.toolbar_hint':   'Select text in the editor and click',
      'book.toolbar_cta':    'AI Tools',
      'book.total_words':    '{n} words',

      // Chapter states
      'ch.pending':  'Pending',
      'ch.writing':  'Writing…',
      'ch.done':     'Done ✓',
      'ch.reviewed': 'Reviewed ✓',

      // Length validator
      'val.short_title':  'Chapter too short to mark as reviewed',
      'val.short_detail': 'A chapter needs at least 800 words. This one has {wc}.',

      // Step names (16)
      'step.1':  'Offer Modeling',
      'step.2':  'Market Research',
      'step.3':  'Buyer Avatars',
      'step.4':  'Sales Angles',
      'step.5':  'Visual Identity',
      'step.6':  'Premium Mockups',
      'step.7':  'Ads Generator',
      'step.8':  'Landing Page',
      'step.9':  'Product Copies',
      'step.10': 'Video Scripts',
      'step.11': 'UGC Prompts',
      'step.12': 'Infoproduct',
      'step.13': 'Upsells + AOV',
      'step.14': 'Email Marketing',
      'step.15': 'Global Export',
      'step.16': 'VIP Campus',

      // Manual de Vuelo — hover tooltips for 16 steps
      'manual.1':  'AI analyzes the real market to find the gaps your competitors left behind. If you try to sell to everyone, you sell to no one.',
      'manual.2':  'Define the "Grand Promise" — what you\'re selling and why it\'s irresistible. It\'s not about selling cheap; it\'s about making the purchase obvious.',
      'manual.3':  'We create psychological profiles of your ideal buyers. Stop selling to "everyone" and start selling to someone with a name, a pain, and a concrete desire.',
      'manual.4':  'We define the right angle: fear, pleasure, or time savings. The perfect hook to enter the buyer\'s mind and double conversion.',
      'manual.5':  'We generate your colors and typography so your brand looks like a $10,000 USD brand from day one.',
      'manual.6':  'We create photorealistic 3D images of your product. What enters through the eyes, sells.',
      'manual.7':  'We design the ads (images) that will stop the scroll on Facebook and Instagram.',
      'manual.8':  'We build your "24/7 salesperson" — a website optimized to convert visits into money.',
      'manual.9':  'The technical and emotional description that goes on your payment button. Copy that transforms attention into sales.',
      'manual.10': 'What to say in your Reels or VSL so people trust you and buy from you.',
      'manual.11': 'Instructions so content creators talk about your product naturally and authentically.',
      'manual.12': 'The mass generator. AI writes the 40–80 pages of your book or course. Professional editor with built-in AI tools.',
      'manual.13': 'We design the "combo". Want fries with that? We increase your average ticket with strategic upsells.',
      'manual.14': 'Email sequences to recover abandoned carts, retain customers, and reactivate dormant leads.',
      'manual.15': 'Step-by-step guide to sell outside your country and get paid in dollars or euros.',
      'manual.16': 'Your access to the advanced strategy to scale from your first $100 to $10,000.',

      // Multi-market form
      'market.section_title': '🌎 Multi-market Configuration',
      'market.section_desc':  'Choose from linguistic markets (Spanish, English, Portuguese-speaking), regions (LATAM, USA, Europe) or specific countries (MX, AR, BR, ES…).',
      'market.primary_label': 'Primary market',
      'market.target_label':  'Target markets',
      // Market choice labels
      'market.HISPANO': '🌎 Spanish-speaking',
      'market.ANGLO':   '🇬🇧 English-speaking',
      'market.LUSO':    '🇧🇷 Portuguese-speaking',
      'market.LATAM':   '🌎 Latin America',
      'market.USA':     '🇺🇸 USA',
      'market.EURO':    '🇪🇺 Europe',
      'market.MX':      '🇲🇽 Mexico',
      'market.AR':      '🇦🇷 Argentina',
      'market.CO':      '🇨🇴 Colombia',
      'market.CL':      '🇨🇱 Chile',
      'market.UY':      '🇺🇾 Uruguay',
      'market.BR':      '🇧🇷 Brazil',
      'market.ES':      '🇪🇸 Spain',
      // Create project form
      'create.submit_btn': 'Build my business with AI →',
      'create.hint':       'Plan A USD29/month: complete workflow + multi-market + scalable tests',
    },

    // ── PORTUGUESE (Brazil / Portugal) ─────────────────────────
    pt: {
      // Navbar
      'nav.account':     'Minha Conta',
      'nav.new_project': '+ Novo Projeto',
      'nav.login':       'Entrar',
      'nav.register':    'Começar Grátis',
      'nav.logout':      'Sair',

      // Sidebar
      'sidebar.title':    'Mapa da Rota',
      'sidebar.subtitle': 'A barra lateral acende à medida que você completa cada módulo.',

      // Missions
      'mission.1.title': 'Missão 1: A Fundação',
      'mission.1.desc':  'Validar se sua ideia vai gerar dinheiro antes de escrever uma única palavra.',
      'mission.2.title': 'Missão 2: A Vitrine',
      'mission.2.desc':  'Sua ideia começa a parecer uma empresa real.',
      'mission.3.title': 'Missão 3: Máquina de Vendas',
      'mission.3.desc':  'Preparamos o discurso para convencer desconhecidos.',
      'mission.4.title': 'Missão 4: Fábrica e Escala',
      'mission.4.desc':  'Produto final e crescimento global.',

      // Common UI
      'ui.what_for':           'Para que serve isso?',
      'ui.done':               '✓ Pronto',
      'ui.next_step':          'Próximo Passo',
      'ui.save':               '💾 Salvar',
      'ui.saved':              '✓ Salvo',
      'ui.generate':           'Gerar com IA',
      'ui.regenerate':         '↻ Regenerar',
      'ui.complete_to_advance':'Conclua e salve para avançar',
      'ui.route_complete':     'Rota principal concluída',
      'ui.completed_pill':     'Concluído',
      'ui.processing_pill':    'Processando',
      'ui.pending_pill':       'Pendente',
      'ui.download_ebook':     '⬇️ Baixar',

      // Reference panel
      'ref.title':    'Referência',
      'ref.subtitle': 'Resumo do passo anterior para não perder o contexto.',

      // Card titles & subtitles
      'card.niche.title':   'Análise de Nicho',
      'card.niche.sub':     'Avatar + Dores + Desejos',
      'card.niche.hint':    'Se você tenta vender para todos, não vende para ninguém. Aqui definimos para quem sua solução dói mais.',
      'card.offer.title':   'Oferta Irresistível',
      'card.offer.sub':     'Preço · Bônus · Garantia',
      'card.offer.hint':    'Agora convertemos o insight em uma oferta irresistível.',
      'card.revenue.title': 'Gestão de Receita',
      'card.revenue.sub':   'Order Bump · Upsell · OTO',
      'card.revenue.hint':  'Otimize o ticket médio antes de escalar o tráfego.',
      'card.outline.title': 'Índice do Infoproduto',
      'card.outline.sub':   'E-book · 10 capítulos',
      'card.outline.hint':  'Com a oferta validada, montamos a estrutura do livro.',
      'card.copy.title':    'Biblioteca de Copies',
      'card.copy.sub':      'Headlines · Hooks · E-mails',
      'card.copy.hint':     'Com o índice pronto, criamos os textos de venda.',

      // Book editor (Step 12)
      'book.title':          'O Infoproduto',
      'book.sub':            'Editor Profissional · 15.000 – 25.000 palavras',
      'book.what_for':       'O gerador em massa. A IA escreve as 40–80 páginas do seu livro ou curso aqui. Escreva capítulo por capítulo ou ative o Modo Fábrica para escrever tudo de uma vez.',
      'book.progress_label': 'Progresso do manuscrito',
      'book.word_goal':      '0 / 15.000 palavras',
      'book.word_min':       'Meta mínima: 15.000',
      'book.index_title':    'Índice',
      'book.select_chapter': 'Selecione um capítulo →',
      'book.write_btn':      '⚡ Escrever com IA',
      'book.writing':        '⚡ Escrevendo…',
      'book.save_btn':       '💾 Salvar',
      'book.reviewed':       'Revisado ✓',
      'book.expand':         '✨ Expandir Seção',
      'book.tone':           '✍️ Mudar Tom',
      'book.example':        '💡 Adicionar Exemplo',
      'book.factory_title':  '🏭 Modo Fábrica',
      'book.factory_btn':    '⚡ Escrever Tudo',
      'book.placeholder':    'Selecione um capítulo do índice à esquerda para começar a escrever…',
      'book.toolbar_hint':   'Selecione texto no editor e clique em',
      'book.toolbar_cta':    'Ferramentas IA',
      'book.total_words':    '{n} palavras',

      // Chapter states
      'ch.pending':  'Pendente',
      'ch.writing':  'Escrevendo…',
      'ch.done':     'Pronto ✓',
      'ch.reviewed': 'Revisado ✓',

      // Length validator
      'val.short_title':  'Capítulo muito curto para marcar como revisado',
      'val.short_detail': 'Um capítulo precisa de no mínimo 800 palavras. Este tem {wc}.',

      // Step names (16)
      'step.1':  'Modelagem de Oferta',
      'step.2':  'Pesquisa de Mercado',
      'step.3':  'Avatares',
      'step.4':  'Ângulos de Venda',
      'step.5':  'Identidade Visual',
      'step.6':  'Mockups Premium',
      'step.7':  'Gerador de Anúncios',
      'step.8':  'Página de Vendas',
      'step.9':  'Copies do Produto',
      'step.10': 'Roteiros de Vídeo',
      'step.11': 'Prompts UGC',
      'step.12': 'Infoproduto',
      'step.13': 'Upsells + AOV',
      'step.14': 'Email Marketing',
      'step.15': 'Exportação Global',
      'step.16': 'Campus VIP',

      // Manual de Vuelo — hover tooltips for 16 steps (Portuguese)
      'manual.1':  'A IA analisa o mercado real para encontrar as lacunas que seus concorrentes deixaram. Se você tenta vender para todos, não vende para ninguém.',
      'manual.2':  'Define a "Grande Promessa" — o que você vai vender e por que é irresistível. Não se trata de vender barato, mas de tornar a compra óbvia.',
      'manual.3':  'Criamos perfis psicológicos dos seus compradores ideais. Pare de vender para "todos" e comece a vender para alguém com nome, dor e desejo concreto.',
      'manual.4':  'Definimos o ângulo certo: medo, prazer ou economia de tempo. O gancho perfeito para entrar na mente do comprador e dobrar a conversão.',
      'manual.5':  'Geramos suas cores e tipografias para que sua marca pareça uma marca premium desde o primeiro dia.',
      'manual.6':  'Criamos imagens 3D fotorrealistas do seu produto. O que entra pelos olhos, vende.',
      'manual.7':  'Criamos os anúncios (imagens) que vão parar o scroll no Facebook e Instagram.',
      'manual.8':  'Construímos seu "vendedor 24/7" — um site otimizado para converter visitas em dinheiro.',
      'manual.9':  'A descrição técnica e emocional que irá no seu botão de pagamento. Texto que transforma atenção em vendas.',
      'manual.10': 'O que dizer nos seus Reels ou VSL para que as pessoas confiem em você e comprem.',
      'manual.11': 'Instruções para que criadores de conteúdo falem do seu produto de forma natural e autêntica.',
      'manual.12': 'O gerador em massa. A IA escreve as 40–80 páginas do seu livro ou curso. Editor profissional com ferramentas de IA integradas.',
      'manual.13': 'Criamos o "combo". Quer batata frita com isso? Aumentamos seu ticket médio com upsells estratégicos.',
      'manual.14': 'Sequências de e-mails para recuperar carrinhos abandonados, fidelizar clientes e reativar leads dormentes.',
      'manual.15': 'Guia passo a passo para vender fora do seu país e receber em dólares ou euros.',
      'manual.16': 'Seu acesso à estratégia avançada para escalar dos seus primeiros R$500 para R$50.000.',

      // Multi-market form
      'market.section_title': '🌎 Configuração Multi-mercado',
      'market.section_desc':  'Escolha entre mercados linguísticos (Hispano, Anglo, Luso-falante), regiões (LATAM, EUA, Europa) ou países específicos (MX, AR, BR, ES…).',
      'market.primary_label': 'Mercado principal',
      'market.target_label':  'Mercados-alvo',
      // Market choice labels
      'market.HISPANO': '🌎 Hispano-falante',
      'market.ANGLO':   '🇬🇧 Anglo-falante',
      'market.LUSO':    '🇧🇷 Luso-falante',
      'market.LATAM':   '🌎 América Latina',
      'market.USA':     '🇺🇸 EUA / USA',
      'market.EURO':    '🇪🇺 Europa',
      'market.MX':      '🇲🇽 México',
      'market.AR':      '🇦🇷 Argentina',
      'market.CO':      '🇨🇴 Colômbia',
      'market.CL':      '🇨🇱 Chile',
      'market.UY':      '🇺🇾 Uruguai',
      'market.BR':      '🇧🇷 Brasil',
      'market.ES':      '🇪🇸 Espanha',
      // Create project form
      'create.submit_btn': 'Construir meu negócio com IA →',
      'create.hint':       'Plano A USD29/mês: workflow completo + multi-mercado + testes escaláveis',
    },
  };

  /**
   * Translate a key with optional variable interpolation.
   * Falls back to Spanish, then returns the raw key if not found.
   * @param {string} key
   * @param {Object} [vars] — e.g. { wc: 450 } replaces {wc} in the string
   */
  function t(key, vars) {
    const lang = window.UI_LANG || 'es';
    let str =
      (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) ||
      (TRANSLATIONS['es'] && TRANSLATIONS['es'][key]) ||
      key;
    if (vars) {
      Object.keys(vars).forEach((k) => {
        str = str.replace(new RegExp('\\{' + k + '\\}', 'g'), vars[k]);
      });
    }
    return str;
  }

  /**
   * Walk the DOM and apply translations to every element that has:
   *   data-i18n      → sets textContent
   *   data-i18n-html → sets innerHTML
   *   data-i18n-ph   → sets placeholder
   *   data-i18n-title→ sets title attribute
   */
  function applyI18n() {
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const val = t(el.dataset.i18n);
      if (val !== el.dataset.i18n) el.textContent = val;
    });
    document.querySelectorAll('[data-i18n-html]').forEach((el) => {
      const val = t(el.dataset.i18nHtml);
      if (val !== el.dataset.i18nHtml) el.innerHTML = val;
    });
    document.querySelectorAll('[data-i18n-ph]').forEach((el) => {
      const val = t(el.dataset.i18nPh);
      if (val !== el.dataset.i18nPh) el.placeholder = val;
    });
    document.querySelectorAll('[data-i18n-title]').forEach((el) => {
      const val = t(el.dataset.i18nTitle);
      if (val !== el.dataset.i18nTitle) el.title = val;
    });
    // Update <html lang> attribute
    const langMap = { es: 'es', en: 'en', pt: 'pt-BR' };
    document.documentElement.lang = langMap[window.UI_LANG] || 'es';
    // Translate <select> options for the primary market field
    const mktSelect = document.getElementById('id_primary_market');
    if (mktSelect) {
      mktSelect.querySelectorAll('option').forEach(function (opt) {
        if (opt.value) {
          const translated = t('market.' + opt.value);
          if (translated !== 'market.' + opt.value) opt.textContent = translated;
        }
      });
    }
  }

  // Expose globally
  window.TRANSLATIONS = TRANSLATIONS;
  window.t = t;
  window.applyI18n = applyI18n;

  // Auto-apply when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyI18n);
  } else {
    applyI18n();
  }
})();
