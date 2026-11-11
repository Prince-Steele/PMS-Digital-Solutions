"""Regression checks for the static PMS site. Install Playwright and Google Chrome.
Run: python tests/check-site.py. Uses a temporary loopback server; sends no messages.
"""
import asyncio,json
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse,parse_qs
from playwright.async_api import async_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.local/design-checks';OUT.mkdir(parents=True,exist_ok=True)
async def main():
 results=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(channel='chrome',headless=True)
  page=await browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
  await page.goto(f'{BASE}/')
  await page.evaluate('document.fonts.ready')
  assert await page.locator('main').evaluate('(el)=>{const ids=[...el.children].map(x=>x.id);return ids.indexOf("pricing")<ids.indexOf("portfolio")}')
  await page.add_style_tag(content='.reveal{opacity:1!important;transform:none!important} *,*::before,*::after{transition:none!important;animation:none!important}')
  await page.locator('.services-trigger').hover()
  await expect(page.locator('#services-dropdown')).to_be_visible()
  await page.screenshot(path=str(OUT/'desktop-coded-services-dropdown.png'))
  await page.locator('#services-dropdown a[href="#pricing"]').click()
  await expect(page).to_have_url(f'{BASE}/#pricing')
  await expect(page.locator('#services-dropdown')).to_be_hidden()
  assert await page.locator('#pricing').evaluate('(el)=>Math.abs(el.getBoundingClientRect().top-88)<3')
  await page.locator('.services-trigger').focus();await page.keyboard.press('ArrowDown')
  await expect(page.locator('#services-dropdown a').first).to_be_focused()
  await page.keyboard.press('Escape')
  await expect(page.locator('#services-dropdown')).to_be_hidden()
  await expect(page.locator('.services-trigger')).to_be_focused()
  results.append('Services dropdown: hover, Pricing navigation, keyboard and Escape passed')
  for index in range(4):
   await page.locator(f'[data-service="{index}"]').click()
   await expect(page.locator('#service-panel')).to_have_attribute('aria-labelledby',['tab-web','tab-ecom','tab-apps','tab-custom'][index])
   await expect(page.locator(f'[data-service="{index}"]')).to_have_attribute('aria-selected','true')
  await page.keyboard.press('ArrowDown')
  await expect(page.locator('[data-service="0"]')).to_be_focused()
  await page.locator('#service-panel [data-quote-type]').click()
  await expect(page.locator('#type')).to_have_value('Business website')
  assert (await page.locator('#details').input_value()).startswith('Interested in: Website Development')
  results.append('All service panels, arrow navigation and enquiry prefill passed')
  await expect(page.locator('[data-currency="JMD"]')).to_have_attribute('aria-pressed','true')
  await expect(page.locator('#pricing-content .plan-amount').first).to_have_text('J$50,000 - J$80,000')
  await page.locator('[data-currency="USD"]').focus();await page.keyboard.press('Enter')
  await expect(page.locator('#pricing-content .plan-amount').first).to_have_text('US$314 - US$502')
  await expect(page.locator('#currency-note')).to_contain_text('Approx. USD')
  await expect(page.locator('#currency-reference')).to_be_visible()
  assert not await page.locator('#pricing-content [data-price]').evaluate_all('(els)=>els.some(el=>el.textContent.includes("J$"))')
  await expect(page.locator('#pricing-content dd').nth(1)).to_have_text('US$57 - US$75 per page')
  await page.locator('[data-pricing="port"]').click()
  await expect(page.locator('#pricing-content .plan-amount').first).to_have_text('US$251 - US$377')
  await page.locator('[data-pricing="biz"]').click()
  await expect(page.locator('#pricing-content .plan-amount').first).to_have_text('US$314 - US$502')
  for _ in range(3):
   await page.locator('[data-currency="JMD"]').click()
   await expect(page.locator('#pricing-content .plan-amount').first).to_have_text('J$50,000 - J$80,000')
   await page.locator('[data-currency="USD"]').click()
  await page.reload();await page.evaluate('document.fonts.ready')
  await expect(page.locator('[data-currency="USD"]')).to_have_attribute('aria-pressed','true')
  await expect(page.locator('#pricing-content .plan-amount').first).to_have_text('US$314 - US$502')
  await page.locator('[data-pricing="port"]').click()
  await page.get_by_role('button',name='Request Professional Portfolio',exact=True).click()
  notes=await page.locator('#details').input_value()
  assert 'J$90,000 - J$130,000' in notes and 'Approx. US$565 - US$816' in notes,notes
  await page.locator('[data-currency="JMD"]').click()
  await expect(page.locator('#pricing-content .plan-amount').first).to_have_text('J$40,000 - J$60,000')
  results.append('Currency selector: default JMD, USD cards/add-ons, keyboard, category switching, no rounding drift, reload persistence and quoted estimates passed')
  for tab in ['port','biz','port']:
   await page.locator(f'[data-pricing="{tab}"]').click()
   await expect(page.locator(f'[data-pricing="{tab}"]')).to_have_attribute('aria-pressed','true')
   assert await page.locator('#pricing-content h3').count()>=4
  await page.locator('#details').fill('My existing project notes.')
  await page.get_by_role('button',name='Request Professional Portfolio',exact=True).click()
  await expect(page.locator('#type')).to_have_value('Portfolio website')
  notes=await page.locator('#details').input_value()
  assert 'Professional Portfolio' in notes and 'My existing project notes.' in notes
  results.append('Both pricing categories, comparison tables and package prefill passed')
  for kind,count in [('live',3),('concept',6),('all',9)]:
   await page.locator(f'[data-filter="{kind}"]').click()
   assert await page.locator('[data-project-kind]:visible').count()==count
  results.append('Portfolio filters passed: 9 total, 3 live projects, 6 concepts')
  await page.evaluate('document.getElementById("enquiry-form").reset()')
  await page.locator('#enquiry-form button[type="submit"]').click()
  assert await page.locator('#enquiry-form [aria-invalid="true"]').count()==4
  await expect(page.locator('#name')).to_be_focused()
  await page.locator('#name').fill('Local design review')
  await page.locator('#email').fill('review@example.com')
  await page.locator('#type').select_option('Business website')
  await page.locator('#business').fill('Review example')
  await page.locator('#budget').select_option('Not sure yet')
  await page.locator('#details').fill('Testing the local project enquiry flow without sending a message.')
  await page.evaluate('window.open=(url)=>{window.testWhatsapp=url;return null}')
  await page.locator('#whatsapp-enquiry').click()
  url=await page.evaluate('window.testWhatsapp');parsed=urlparse(url)
  assert parsed.netloc=='wa.me' and parsed.path=='/18768205761'
  assert 'review@example.com' in parse_qs(parsed.query)['text'][0]
  assert 'without sending a message' in parse_qs(parsed.query)['text'][0]
  await expect(page.locator('#enquiry-status')).to_contain_text('review and send')
  # Headless Chrome does not send mail; this only checks draft creation feedback.
  await page.locator('#enquiry-form button[type="submit"]').click()
  await expect(page.locator('#enquiry-status')).to_contain_text('Review the draft and press send')
  assert await page.locator('#enquiry-form [aria-invalid="true"]').count()==0
  results.append('Form validation and encoded email/WhatsApp draft actions passed; no messages sent')
  await page.set_viewport_size({'width':390,'height':844})
  await page.evaluate('scrollTo(0,0)')
  await page.locator('#menu-toggle').click()
  await expect(page.locator('#mobile-menu')).to_have_attribute('aria-hidden','false')
  await expect(page.locator('#mobile-menu')).to_have_css('opacity','1')
  assert await page.locator('#mobile-menu ul a').all_text_contents()==['01Home','02Services','03Pricing','04Portfolio','05About','06Contact']
  assert await page.locator('#mobile-services-dropdown,.mobile-services-toggle').count()==0
  hit_targets=await page.locator('#mobile-menu ul a').evaluate_all('''links=>links.map(a=>{const r=a.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&a.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))})''')
  assert all(hit_targets),hit_targets
  await page.screenshot(path=str(OUT/'mobile-coded-services-menu.png'))
  await page.locator('#mobile-menu a[href="#pricing"]').click()
  await expect(page).to_have_url(f'{BASE}/#pricing')
  await expect(page.locator('#mobile-menu')).to_have_attribute('aria-hidden','true')
  assert not await page.locator('main').evaluate('(el)=>el.inert')
  await page.locator('#menu-toggle').click();await page.keyboard.press('Escape')
  await expect(page.locator('#menu-toggle')).to_be_focused()
  await expect(page.locator('#menu-toggle')).to_have_attribute('aria-expanded','false')
  results.append('Mobile menu: six visible direct links, unclipped hit targets, Pricing navigation, Escape and focus restoration passed')
  # Real touch hit-testing prevents clipped/translated links from passing via auto-scrolling clicks.
  touch=await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='no-preference')
  phone=await touch.new_page();await phone.goto(f'{BASE}/');await phone.evaluate('document.fonts.ready')
  for target in ['home','services','pricing','portfolio','about','contact']:
   await phone.locator('#menu-toggle').tap()
   await expect(phone.locator('#mobile-menu')).to_have_css('opacity','1')
   await expect(phone.locator('#mobile-menu')).to_have_attribute('aria-hidden','false')
   assert not await phone.locator('#mobile-menu').evaluate('(e)=>e.inert')
   hit_targets=await phone.locator('#mobile-menu ul a').evaluate_all('''links=>links.map(a=>{const r=a.getBoundingClientRect();return r.top>=76&&r.bottom<=innerHeight&&a.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))})''')
   assert all(hit_targets),(target,hit_targets)
   await phone.locator(f'#mobile-menu ul a[href="#{target}"]').tap()
   await expect(phone).to_have_url(f'{BASE}/#{target}')
   await expect(phone.locator('#menu-toggle')).to_have_attribute('aria-expanded','false')
   assert await phone.locator('#mobile-menu').evaluate('(e)=>e.inert')
   assert not await phone.locator('main').evaluate('(e)=>e.inert')
   assert await phone.evaluate('document.body.style.overflow')==''
  # Short screens can scroll inside the menu without moving the page behind it.
  await phone.set_viewport_size({'width':844,'height':390})
  await phone.locator('#menu-toggle').tap();await expect(phone.locator('#mobile-menu')).to_have_css('opacity','1')
  scroll=await phone.evaluate('scrollY')
  await phone.locator('#mobile-menu').evaluate('(e)=>e.scrollTop=e.scrollHeight')
  assert await phone.locator('#mobile-menu').evaluate('(e)=>e.scrollTop>0')
  assert await phone.evaluate('scrollY')==scroll
  await phone.locator('.mobile-menu-footer a').tap()
  await expect(phone).to_have_url(f'{BASE}/#contact')
  await expect(phone.locator('#menu-toggle')).to_have_attribute('aria-expanded','false')
  await phone.set_viewport_size({'width':390,'height':844})
  await phone.locator('#menu-toggle').tap()
  await phone.set_viewport_size({'width':1200,'height':900})
  await expect(phone.locator('#menu-toggle')).to_have_attribute('aria-expanded','false')
  assert not await phone.locator('main').evaluate('(e)=>e.inert')
  assert await phone.evaluate('document.body.style.overflow')==''
  await touch.close()
  results.append('Touch navigation: all six routes, repeated open/close, landscape scrolling and desktop resize cleanup passed')
  for width in [320,390,768,1024,1440]:
   await page.set_viewport_size({'width':width,'height':844 if width<800 else 1000})
   await page.goto(f'{BASE}/');await page.evaluate('document.fonts.ready')
   for tab in ['biz','port']:
    await page.locator(f'[data-pricing="{tab}"]').click()
    for currency in ['USD','JMD']:
     await page.locator(f'[data-currency="{currency}"]').click()
     dimensions=await page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})')
     assert dimensions['viewport']==dimensions['document'],(width,tab,currency,dimensions)
     buttons=await page.locator('.pricing-controls button').evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right}})')
     assert all(b['left']>=0 and b['right']<=width for b in buttons),(width,buttons)
   image=await page.locator('.hero-art').evaluate('(img)=>({loaded:img.complete&&img.naturalWidth>0,width:img.getBoundingClientRect().width,height:img.getBoundingClientRect().height})')
   assert image['loaded'] and image['width']==width
   await page.evaluate('scrollTo(0,0)')
   assert await page.locator('#home .hero-layout').evaluate('(el)=>el.getBoundingClientRect().bottom>=innerHeight-1')
  results.append('320, 390, 768, 1024 and 1440px: no horizontal page overflow; full-screen hero passed')
  for name,target in [('services','services'),('portfolio','portfolio'),('about','about'),('contact','contact')]:
   await page.goto(f'{BASE}/{name}.html')
   await expect(page).to_have_url(f'{BASE}/index.html#{target}')
  assert not errors,errors
  results.append('Legacy page links and browser runtime checks passed')
  blocked=await browser.new_context()
  await blocked.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw new DOMException("Storage disabled","SecurityError")}})')
  fallback=await blocked.new_page();await fallback.goto(f'{BASE}/')
  await expect(fallback.locator('[data-currency="JMD"]')).to_have_attribute('aria-pressed','true')
  await fallback.locator('[data-currency="USD"]').click()
  await expect(fallback.locator('#pricing-content .plan-amount').first).to_have_text('US$314 - US$502')
  await blocked.close()
  results.append('Currency selection works when browser storage is unavailable')
  await browser.close()
 report={'checks':results,'errors':errors}
 (OUT/'interaction-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report,indent=2))
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass

if __name__=='__main__':
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
 Thread(target=server.serve_forever,daemon=True).start()
 BASE=f'http://127.0.0.1:{server.server_port}'
 try: asyncio.run(main())
 finally:
  server.shutdown();server.server_close()
