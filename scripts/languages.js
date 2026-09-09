/* Site-wide automatic translation, powered by GTranslate's website widget. */
(() => {
  const header = document.querySelector('header.site, .bhead');
  if (!header) return;
  const languages = {en:'EN',es:'ES',pt:'PT','zh-CN':'中文',it:'IT',fr:'FR',ar:'عربي',de:'DE',ja:'日本語',ko:'한국어'};
  const messages = {
    en:['Language','Automatic translation','Translating…','Translation unavailable. Please try again.'],
    es:['Idioma','Traducción automática','Traduciendo…','Traducción no disponible. Inténtalo de nuevo.'],
    pt:['Idioma','Tradução automática','Traduzindo…','Tradução indisponível. Tente novamente.'],
    'zh-CN':['语言','自动翻译','正在翻译…','翻译暂不可用，请重试。'],
    it:['Lingua','Traduzione automatica','Traduzione in corso…','Traduzione non disponibile. Riprova.'],
    fr:['Langue','Traduction automatique','Traduction en cours…','Traduction indisponible. Réessayez.'],
    ar:['اللغة','ترجمة آلية','جارٍ الترجمة…','الترجمة غير متاحة. يُرجى المحاولة مجددًا.'],
    de:['Sprache','Automatische Übersetzung','Wird übersetzt…','Übersetzung nicht verfügbar. Bitte erneut versuchen.'],
    ja:['言語','自動翻訳','翻訳中…','翻訳できません。もう一度お試しください。'],
    ko:['언어','자동 번역','번역 중…','번역할 수 없습니다. 다시 시도해 주세요.']
  };
  // Short navigation labels need their trading context preserved: 'Produce'
  // means fruit and vegetables, rather than the verb 'to manufacture'.
  const labels = {
    en:['Home','Produce','Services','About','Blog','Contact','Request a quote','Work with us','View details'],
    es:['Inicio','Frutas y verduras','Servicios','Nosotros','Blog','Contacto','Solicitar cotización','Trabaja con nosotros','Ver detalles'],
    pt:['Início','Frutas e verduras','Serviços','Sobre nós','Blog','Contato','Solicitar cotação','Trabalhe conosco','Ver detalhes'],
    'zh-CN':['首页','果蔬产品','服务','关于我们','资讯','联系我们','获取报价','与我们合作','查看详情'],
    it:['Home','Frutta e verdura','Servizi','Chi siamo','Blog','Contatti','Richiedi un preventivo','Collabora con noi','Vedi dettagli'],
    fr:['Accueil','Fruits et légumes','Services','À propos','Blog','Contact','Demander un devis','Travaillons ensemble','Voir les détails'],
    ar:['الرئيسية','الفواكه والخضروات','خدماتنا','من نحن','المقالات','اتصل بنا','اطلب عرض سعر','تعاون معنا','عرض التفاصيل'],
    de:['Startseite','Obst und Gemüse','Leistungen','Über uns','Blog','Kontakt','Angebot anfordern','Mit uns arbeiten','Details ansehen'],
    ja:['ホーム','青果物','サービス','会社案内','ブログ','お問い合わせ','見積もりを依頼','お取引について','詳細を見る'],
    ko:['홈','과일 및 채소','서비스','회사 소개','블로그','문의','견적 요청','거래 문의','상세 보기']
  };
  const localized = [];
  document.querySelectorAll('header nav a, .btn, .bbtn, .produce-details').forEach(el => {
    const index = labels.en.findIndex(label => el.textContent.replace('↗','').trim().toLowerCase() === label.toLowerCase());
    if (index < 0) return;
    el.classList.add('notranslate'); el.setAttribute('translate','no');
    const node = [...el.childNodes].find(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
    if (node) localized.push({node,index});
  });
  let current = 'en', pending = null, job = 0;
  try { const saved = JSON.parse(localStorage.getItem('__GT_TRANSLATE_LANGS')); if (languages[saved?.tgtLang]) pending = saved.tgtLang; } catch {}
  const menu = document.createElement('details');
  menu.className = 'language-menu notranslate';
  menu.setAttribute('translate','no');
  menu.innerHTML = `<summary aria-label="Choose language"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 6.5h14M5 17.5h14"/></svg><span class="language-code">EN</span><span aria-hidden="true">⌄</span></summary><div class="language-panel"><strong class="language-label">Language</strong><div class="gtranslate_wrapper"></div><p class="language-status" role="status" aria-live="polite">Automatic translation</p><button class="language-retry" type="button" hidden>Retry</button></div>`;
  header.insertBefore(menu, header.querySelector(':scope > .btn'));
  const status = menu.querySelector('.language-status'), retry = menu.querySelector('.language-retry');
  const text = () => messages[current];
  function apply(lang) {
    current = lang;
    localized.forEach(({node,index}) => { node.textContent = labels[lang][index] + ' '; });
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    menu.querySelector('.language-code').textContent = languages[lang];
    menu.querySelector('.language-label').textContent = text()[0];
    menu.querySelector('summary').setAttribute('aria-label', text()[0]);
    const select = menu.querySelector('select');
    if (select) { select.value = 'en|' + lang; select.setAttribute('aria-label', text()[0]); }
    status.textContent = text()[1];
    menu.removeAttribute('aria-busy');
    retry.hidden = true;
    // Translation changes text wrapping and therefore scroll scene positions.
    requestAnimationFrame(() => { window.lenis?.resize(); window.ScrollTrigger?.refresh(); window.dispatchEvent(new Event('resize')); });
  }
  function failed(lang) {
    menu.removeAttribute('aria-busy');
    status.textContent = messages[lang][3];
    retry.hidden = false;
    retry.textContent = messages[lang][0] + ' ↻';
    menu.open = true;
  }
  async function translate(lang) {
    const request = ++job;
    pending = lang;
    retry.hidden = true;
    menu.setAttribute('aria-busy', 'true');
    status.textContent = messages[lang][2];
    const started = Date.now();
    // The provider widget loads its engine lazily. Wait for readiness, including
    // on a first visit, instead of losing the user's first language selection.
    if (!window.gt_translate_script) {
      const engineScript = document.createElement('script');
      engineScript.src = 'https://cdn.gtranslate.net/widgets/latest/lib.min.js';
      window.gt_translate_script = engineScript;
      document.head.appendChild(engineScript);
    }
    while (!window.__GT?.translator?.libReady) {
      if (request !== job) return;
      if (Date.now() - started > 20000) { window.gt_translate_script?.remove(); window.gt_translate_script = null; failed(lang); return; }
      await new Promise(resolve => setTimeout(resolve,100));
    }
    if (request !== job) return;
    const engine = window.__GT.translator;
    let restoredLanguage;
    try { restoredLanguage = JSON.parse(localStorage.getItem('__GT_TRANSLATE_LANGS'))?.tgtLang; } catch {}
    // A saved choice is already being translated by the engine on page load.
    // Starting it twice can restore the DOM underneath the first completion.
    if (lang === 'en' || restoredLanguage !== lang) engine.translate('en', lang);
    while (lang !== 'en' && !engine.finished) {
      if (request !== job) return;
      if (engine.error || Date.now() - started > 45000) { failed(lang); return; }
      await new Promise(resolve => setTimeout(resolve,150));
    }
    if (request === job) apply(lang);
  }
  window.gtranslateSettings = {default_language:'en',languages:Object.keys(languages),native_language_names:true,detect_browser_language:false,wrapper_selector:'.gtranslate_wrapper',select_language_label:'Language'};
  let widget;
  function load() {
    if (widget) return;
    widget = document.createElement('script');
    widget.src = 'https://cdn.gtranslate.net/widgets/latest/dropdown.js';
    widget.async = true;
    widget.onload = () => {
      const select = menu.querySelector('select');
      select?.querySelector('option[value=""]')?.remove();
      if (pending) translate(pending);
    };
    widget.onerror = () => { widget.remove(); widget = null; failed(pending || current); };
    document.head.appendChild(widget);
  }
  menu.addEventListener('toggle', () => { if (menu.open) load(); });
  menu.addEventListener('change', event => {
    if (event.target.matches('.gt_selector')) {
      event.stopImmediatePropagation();
      const lang = event.target.value.split('|')[1];
      if (languages[lang]) translate(lang);
    }
  }, true);
  retry.addEventListener('click', () => { if (window.doGTranslate) translate(pending || current); else load(); });
  document.addEventListener('click', event => { if (!menu.contains(event.target)) menu.open = false; });
  menu.addEventListener('keydown', event => { if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); } });
  document.querySelectorAll('.logo, .blogo, a[href^="mailto:"], a[href^="tel:"], canvas').forEach(el => { el.classList.add('notranslate'); el.setAttribute('translate','no'); });
  if (pending) load();
})();
