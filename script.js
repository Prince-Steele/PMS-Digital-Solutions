/* PMS Digital Solutions — native interactions for the Figma implementation. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.documentElement.classList.add('js');

  const header = $('#site-header');
  const menu = $('#mobile-menu');
  const toggle = $('#menu-toggle');
  const main = $('main');
  const footer = $('footer');
  const home = $('#home');
  const headerProgress = $('#scroll-progress');
  const servicesTrigger = $('.services-trigger');
  const navLinks = $$('nav[aria-label="Primary"] a, #mobile-menu ul a');
  const sections = $$('main > section[id]');
  let menuOpen = false;
  const serviceDropdowns = $$('[data-services-toggle]').map(button => ({button,panel:document.getElementById(button.getAttribute('aria-controls'))}));
  function setServiceDropdown(which, open, focus = false) {
    serviceDropdowns.forEach(({button,panel}) => {
      const expanded = button.dataset.servicesToggle === which && open;
      button.setAttribute('aria-expanded',String(expanded));
      panel.hidden = !expanded;
      if (expanded && focus) $('a',panel).focus();
    });
  }
  serviceDropdowns.forEach(({button,panel}) => {
    button.addEventListener('click',event=>{
      const mouseHover = button.dataset.servicesToggle==='desktop' && event.detail>0 && matchMedia('(hover:hover)').matches;
      setServiceDropdown(button.dataset.servicesToggle,mouseHover || button.getAttribute('aria-expanded')!=='true');
    });
    button.addEventListener('keydown',event=>{
      if (event.key==='ArrowDown') {event.preventDefault();setServiceDropdown(button.dataset.servicesToggle,true,true);}
    });
    const wrapper=button.closest('.nav-services');
    if (wrapper) {
      wrapper.addEventListener('pointerenter',event=>{if(event.pointerType==='mouse')setServiceDropdown('desktop',true);});
      wrapper.addEventListener('pointerleave',()=>{if(!wrapper.contains(document.activeElement))setServiceDropdown('desktop',false);});
      wrapper.addEventListener('focusout',event=>{if(!wrapper.contains(event.relatedTarget))setServiceDropdown('desktop',false);});
    }
  });
  document.addEventListener('click',event=>{if(!event.target.closest('.nav-services'))setServiceDropdown('desktop',false);});
  function setMenu(open, restoreFocus = true) {
    menuOpen = open;
    setServiceDropdown('desktop',false);
    header.classList.toggle('over-hero', !open && home.getBoundingClientRect().bottom > header.offsetHeight + 90);
    menu.classList.toggle('is-open', open);
    menu.setAttribute('aria-hidden', String(!open));
    menu.inert = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    toggle.innerHTML = open
      ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>'
      : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M4 8h16M4 16h16"/></svg>';
    $$('a', menu).forEach(a => a.tabIndex = open && !a.closest('[hidden]') ? 0 : -1);
    document.body.style.overflow = open ? 'hidden' : '';
    main.inert = open;
    footer.inert = open;
    if (open) {menu.scrollTop = 0;$('a', menu).focus({preventScroll:true});}
    else if (restoreFocus) toggle.focus({preventScroll:true});
  }
  toggle.addEventListener('click', () => setMenu(!menuOpen));
  document.addEventListener('keydown', event => {
    const expanded=serviceDropdowns.find(({panel})=>!panel.hidden);
    if(event.key==='Escape' && expanded) {
      event.preventDefault();setServiceDropdown('desktop',false);expanded.button.focus();return;
    }
    if (!menuOpen) return;
    if (event.key === 'Escape') {event.preventDefault();setMenu(false);return;}
    if (event.key !== 'Tab') return;
    const focusable = [toggle, ...$$('a,button', menu).filter(el=>el.tabIndex>=0 && !el.closest('[hidden]'))];
    const index = focusable.indexOf(document.activeElement);
    if (event.shiftKey && index <= 0) {event.preventDefault();focusable.at(-1).focus();}
    else if (!event.shiftKey && (index === focusable.length - 1 || index < 0)) {event.preventDefault();toggle.focus();}
  });
  const desktop = matchMedia('(min-width:1024px)');
  desktop.addEventListener('change', e => {if (e.matches && menuOpen) setMenu(false, false);});

  function go(id, focus = false) {
    const target = document.getElementById(id);
    if (!target) return;
    setServiceDropdown('desktop',false);
    if (menuOpen) setMenu(false, false);
    history.replaceState(null, '', `#${id}`);
    target.scrollIntoView({behavior: reduced.matches ? 'instant' : 'smooth', block:'start'});
    if (focus) {target.tabIndex = -1;target.focus({preventScroll:true});}
  }
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor) {event.preventDefault();go(anchor.getAttribute('href').slice(1), true);}
    const scroll = event.target.closest('[data-scroll]');
    if (scroll) go(scroll.dataset.scroll, true);
    const quote = event.target.closest('[data-quote-type]');
    if (quote) {
      const details = $('#details');
      $('#type').value = quote.dataset.quoteType;
      const existing = details.value.replace(/^(Package|Interested in):[^\n]*(?:\n\n)?/, '').trim();
      details.value = quote.dataset.quoteNote + '\n\n' + existing;
      $('#enquiry-status').hidden = true;
      go('contact');
    }
  });

  const revealObserver = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) {entry.target.classList.add('in');revealObserver.unobserve(entry.target);}
  }), {threshold:0.12, rootMargin:'0px 0px -6% 0px'});
  function reveal(root = document) {$$('.reveal:not(.in)', root).forEach(el => revealObserver.observe(el));}
  reveal();

  function startEffects() {
    document.documentElement.classList.add('effects-ready');
    const waveObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      entry.target.classList.toggle('waves-active', entry.isIntersecting);
      if (entry.isIntersecting && entry.target.classList.contains('marquee-wrap')) {
        $$('img[loading="lazy"]',entry.target).forEach(image => image.loading = 'eager');
      }
    }), {rootMargin:'80px 0px'});
    $$('.ambient-waves').forEach(layer => waveObserver.observe(layer.parentElement));
    waveObserver.observe($('.marquee-wrap'));
  }
  const queueEffects = () => 'requestIdleCallback' in window
    ? requestIdleCallback(startEffects, {timeout:1500}) : setTimeout(startEffects, 100);
  if (document.readyState === 'complete') queueEffects();
  else addEventListener('load', queueEffects, {once:true});

  const serviceTabs = $$('[data-service]');
  const serviceList = serviceTabs[0].parentElement;
  const servicePanelHome = $('#service-panel').parentElement;
  serviceList.classList.add('service-list');
  servicePanelHome.classList.add('service-panel-home');
  const servicePanels = [$('#service-panel').cloneNode(true), ...[1,2,3].map(index => $(`#service-template-${index}`).content.firstElementChild)];
  let selectedService = 0;
  let mobileServiceOpen = false;
  serviceTabs.forEach(tab => {
    tab.lastElementChild.classList.add('service-meta');
    tab.lastElementChild.insertAdjacentHTML('beforeend', '<svg class="service-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>');
  });
  function renderService() {
    const mobile = !desktop.matches;
    serviceList.setAttribute('role', mobile ? 'group' : 'tablist');
    if (mobile) serviceList.removeAttribute('aria-orientation');
    else serviceList.setAttribute('aria-orientation', 'vertical');
    serviceTabs.forEach((tab, i) => {
      const active = i === selectedService && (!mobile || mobileServiceOpen);
      tab.dataset.active = String(active);
      tab.tabIndex = mobile || i === selectedService ? 0 : -1;
      tab.setAttribute('role', mobile ? 'button' : 'tab');
      tab.removeAttribute(mobile ? 'aria-selected' : 'aria-expanded');
      tab.setAttribute(mobile ? 'aria-expanded' : 'aria-selected', String(active));
    });
    const panel = servicePanels[selectedService].cloneNode(true);
    panel.setAttribute('role', mobile ? 'region' : 'tabpanel');
    panel.hidden = mobile && !mobileServiceOpen;
    $('#service-panel').remove();
    if (mobile) serviceTabs[selectedService].after(panel);
    else servicePanelHome.append(panel);
  }
  function selectService(index, focus = false) {
    if (!desktop.matches) mobileServiceOpen = selectedService !== index || !mobileServiceOpen;
    selectedService = index;
    renderService();
    requestMeasure();
    if (focus) serviceTabs[index].focus();
  }
  renderService();
  desktop.addEventListener('change', () => {renderService();requestMeasure();});
  serviceTabs.forEach((tab, i) => {
    tab.addEventListener('click', () => selectService(i));
    tab.addEventListener('keydown', event => {
      if (!desktop.matches) return;
      let next = i;
      if (['ArrowDown','ArrowRight'].includes(event.key)) next = (i + 1) % serviceTabs.length;
      else if (['ArrowUp','ArrowLeft'].includes(event.key)) next = (i + serviceTabs.length - 1) % serviceTabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = serviceTabs.length - 1;
      else return;
      event.preventDefault();selectService(next, true);
    });
  });
  const pricingContent = $('#pricing-content');
  const pricingTemplates = {biz:document.createElement('template'),port:$('#pricing-template-port')};
  pricingTemplates.biz.content.append(...[...pricingContent.childNodes].map(node => node.cloneNode(true)));
  const currencyControl = $('.currency-control');
  const currencyButtons = $$('[data-currency]');
  const currencyNote = $('#currency-note');
  const currencyReference = $('#currency-reference');
  // Dated BOJ reference; JMD remains the canonical price. No live rate request blocks rendering.
  const usdJmdRate = Number(currencyControl.dataset.usdJmdRate);
  const priceNumber = new Intl.NumberFormat('en-US', {maximumFractionDigits:0});
  let pricingCurrency = 'JMD';
  function usdEstimate(text) {
    return text.replace(/J\$([\d,]+)/g, (_, amount) => 'US$' + priceNumber.format(Number(amount.replaceAll(',', '')) / usdJmdRate));
  }
  function renderPricingCurrency() {
    const usd = pricingCurrency === 'USD';
    $$('[data-price]', pricingContent).forEach(price => {
      price.dataset.jmd ||= price.textContent;
      price.textContent = usd ? usdEstimate(price.dataset.jmd) : price.dataset.jmd;
    });
    $$('[data-quote-note]', pricingContent).forEach(button => {
      button.dataset.quoteJmd ||= button.dataset.quoteNote;
      const original = button.dataset.quoteJmd;
      const amount = original.match(/\(([^)]+)\)/)?.[1];
      button.dataset.quoteNote = usd && amount ? `${original} · Approx. ${usdEstimate(amount)}` : original;
    });
    currencyButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.currency === pricingCurrency)));
    currencyNote.textContent = usd ? 'Approx. USD · Based on JMD prices.' : 'Prices in Jamaican dollars (JMD).';
    currencyReference.hidden = !usd;
  }
  try {
    if (localStorage.getItem('pms-pricing-currency') === 'USD') pricingCurrency = 'USD';
  } catch { /* Pricing remains usable when browser storage is unavailable. */ }
  currencyControl.hidden = false;
  renderPricingCurrency();
  currencyButtons.forEach(button => button.addEventListener('click', () => {
    pricingCurrency = button.dataset.currency;
    renderPricingCurrency();
    try { localStorage.setItem('pms-pricing-currency', pricingCurrency); } catch { /* Optional preference only. */ }
    requestMeasure();
  }));
  $$('[data-pricing]').forEach(button => button.addEventListener('click', () => {
    const tab = button.dataset.pricing;
    $$('[data-pricing]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    pricingContent.replaceChildren(pricingTemplates[tab].content.cloneNode(true));
    renderPricingCurrency();
    reveal(pricingContent);
    requestMeasure();
  }));
  $$('[data-filter]').forEach(button => button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    $$('[data-filter]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    $$('[data-project-kind]').forEach(card => {
      card.hidden = filter !== 'all' && card.dataset.projectKind !== filter;
      if (!card.hidden) card.classList.add('in');
    });
    requestMeasure();
  }));

  const timeline = $('#process-timeline');
  const steps = $$('[data-process-step]');
  const timelineProgress = $('#process-progress');
  let pending = false;
  let needsMeasure = true;
  let layout = {};
  let activeSection = '';
  let lastStep = -1;
  function requestMeasure() {needsMeasure = true; requestScroll();}
  function measureLayout() {
    const scroll = window.scrollY;
    const sectionBounds = sections.map(section => {
      const bounds = section.getBoundingClientRect();
      return {id:section.id,top:bounds.top + scroll,bottom:bounds.bottom + scroll};
    });
    const about = sectionBounds.find(section => section.id === 'about');
    const timelineVisible = about.top < scroll + innerHeight * 2 && about.bottom > scroll - innerHeight;
    const bounds = timelineVisible ? timeline.getBoundingClientRect() : {top:Infinity,height:1};
    layout = {
      height:document.documentElement.scrollHeight - innerHeight,
      viewport:innerHeight,
      header:header.offsetHeight,
      homeBottom:home.getBoundingClientRect().bottom + scroll,
      timelineTop:bounds.top + scroll,
      timelineHeight:bounds.height,
      sections:sectionBounds,
      aboutTop:about.top,
      aboutBottom:about.bottom,
      timelineMeasured:timelineVisible,
    };
    needsMeasure = false;
  }
  function updateScroll() {
    pending = false;
    if (!needsMeasure && !layout.timelineMeasured && layout.aboutTop < scrollY + innerHeight * 2 && layout.aboutBottom > scrollY - innerHeight) needsMeasure = true;
    if (needsMeasure) measureLayout();
    const scroll = window.scrollY;
    header.classList.toggle('is-scrolled', scroll > 24);
    header.classList.toggle('over-hero', !menuOpen && layout.homeBottom - scroll > layout.header + 90);
    headerProgress.style.transform = `scaleX(${layout.height > 0 ? scroll / layout.height : 0})`;
    let active = 'home';
    for (const section of layout.sections) if (section.top <= scroll + layout.viewport * .5) active = section.id;
    if (active !== activeSection) {
      activeSection = active;
      if(active==='services'||active==='pricing')servicesTrigger.setAttribute('aria-current','location');else servicesTrigger.removeAttribute('aria-current');
      navLinks.forEach(a => {
        const location = active === 'pricing' && !a.closest('#mobile-menu') ? 'services' : active;
        if (a.getAttribute('href') === `#${location}`) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');
      });
    }
    const progress = Math.min(1, Math.max(0, (scroll + layout.viewport * .62 - layout.timelineTop) / layout.timelineHeight));
    if (layout.timelineTop < scroll + layout.viewport && layout.timelineTop + layout.timelineHeight > scroll) timelineProgress.style.transform = `scaleY(${progress})`;
    const completed = reduced.matches ? steps.length - 1 : Math.floor((progress + .02) * (steps.length - 1));
    if (completed !== lastStep) {lastStep = completed;steps.forEach((step, i) => step.dataset.done = String(i <= completed));}
  }
  function requestScroll() {if (!pending) {pending = true;requestAnimationFrame(updateScroll);}}
  addEventListener('scroll', requestScroll, {passive:true});
  addEventListener('resize', requestMeasure);
  new ResizeObserver(requestMeasure).observe(document.body);
  document.fonts.ready.then(requestMeasure);
  reduced.addEventListener('change', () => {lastStep = -1; requestScroll();});
  updateScroll();

  const form = $('#enquiry-form');
  const status = $('#enquiry-status');
  const errorMessages = {name:'Please enter your name',email:'Please enter a valid email',type:'Please choose a project type',details:'Tell us a little about your project (at least 10 characters)'};
  function clearError(field) {
    field.setAttribute('aria-invalid','false');field.removeAttribute('aria-describedby');
    document.getElementById(`${field.id}-err`)?.remove();status.hidden = true;
  }
  $$('input,select,textarea',form).forEach(field => field.addEventListener('input',()=>clearError(field)));
  function validate() {
    let first = null;
    for (const field of $$('[required]',form)) {
      clearError(field);
      const value=field.value.trim();
      const invalid = !value || (field.type==='email' && !/^\S+@\S+\.\S+$/.test(value)) || (field.id==='details' && value.length<10);
      if (!invalid) continue;
      const error=document.createElement('p');error.id=`${field.id}-err`;error.className='field-error';error.textContent=errorMessages[field.id];error.setAttribute('role','alert');
      field.after(error);field.setAttribute('aria-invalid','true');field.setAttribute('aria-describedby',error.id);first ||= field;
    }
    first?.focus();return !first;
  }
  function enquiry() {
    const values=Object.fromEntries(new FormData(form));
    return {subject:`Project enquiry: ${values.type}${values.business?' - '+values.business:''}`,body:`Hello PMS Digital Solutions,\n\nName: ${values.name}\nBusiness: ${values.business||'-'}\nEmail: ${values.email}\nProject type: ${values.type}\nBudget: ${values.budget||'Not sure yet'}\n\nProject details:\n${values.details}`};
  }
  form.addEventListener('submit', event => {
    event.preventDefault();if(!validate()) return;
    const {subject,body}=enquiry();
    location.href=`mailto:pmsdigitalsolutions63@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    status.textContent='Your email app should open with the enquiry. Review the draft and press send there. If no app opens, use WhatsApp or email pmsdigitalsolutions63@gmail.com directly.';status.hidden=false;
  });
  $('#whatsapp-enquiry').addEventListener('click', () => {
    if(!validate()) return;
    window.open(`https://wa.me/18768205761?text=${encodeURIComponent(enquiry().body)}`,'_blank','noopener,noreferrer');
    status.textContent='Continue in WhatsApp to review and send your enquiry.';status.hidden=false;
  });
  const params=new URLSearchParams(location.search);
  const selected=params.get('package')||params.get('service')||params.get('selected');
  if(selected) {
    $('#details').value=`Interested in: ${selected}\n\n`;
    if(params.get('type')==='package' || params.has('package')) $('#type').value=/portfolio/i.test(selected)?'Portfolio website':'Business website';
  }
})();
