"""Refresh generated first-screen CSS after editing style.css. Requires Playwright/Chrome."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome')
            page = browser.new_page(viewport={'width':1440,'height':900})
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='networkidle')
            critical = page.evaluate(r'''() => {
              const above = new Set([document.documentElement,document.body,
                ...document.querySelectorAll('#home,#home *,#site-header,#site-header *,#mobile-menu,#mobile-menu *,body>div,main')]);
              function matches(rule) {
                if (rule.style.getPropertyValue('content-visibility') || rule.style.getPropertyValue('--section-height')) return true;
                const candidate = rule.selectorText
                  .replace(/::[a-z-]+(?:\([^)]*\))?/gi,'')
                  .replace(/:(hover|active|focus|focus-visible|focus-within|visited|disabled|enabled)\b/g,'')
                  .replace(/\.(is-open|is-scrolled|over-hero|effects-ready|js|in)\b/g,'')
                  .replace(/\[aria-expanded=["']true["']\]/g,'[aria-expanded]');
                try {return [...document.querySelectorAll(candidate)].some(el=>above.has(el));}
                catch {return true;}
              }
              function visit(rules) {
                let result='';
                for (const rule of rules) {
                  if (rule.selectorText) {if(matches(rule))result+=rule.cssText;}
                  else if (rule.type===CSSRule.KEYFRAMES_RULE) continue;
                  else if (rule.cssRules) {
                    const body=visit(rule.cssRules);
                    if(body)result+=rule.cssText.slice(0,rule.cssText.indexOf('{')+1)+body+'}';
                  } else result+=rule.cssText;
                }
                return result;
              }
              return visit([...document.styleSheets].find(sheet=>sheet.href?.endsWith('/style.css')).cssRules);
            }''')
            critical = critical.replace(f'http://127.0.0.1:{server.server_port}/', '')
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    path=ROOT/'index.html'
    html=path.read_text(encoding='utf-8')
    html=re.sub(r'<style id="critical-css">.*?</style>','',html,flags=re.S)
    html=re.sub(r'<noscript data-full-styles>.*?</noscript>','',html,flags=re.S)
    html=re.sub(r'<link\b[^>]*\bas="font"[^>]*>','',html)
    html=re.sub(r'<link\b(?=[^>]*\bhref="style\.css")[^>]*>', '',html)
    marker='</head>'
    styles=f'<style id="critical-css">{critical}</style><link rel="preload" as="style" href="style.css" fetchpriority="low" data-full-styles onload="this.onload=null;this.rel=\'stylesheet\'"><noscript data-full-styles><link rel="stylesheet" href="style.css"></noscript>'
    html=html.replace(marker,styles+marker)
    html='\n'.join(line.rstrip() for line in html.splitlines())+'\n'
    path.write_text(html,encoding='utf-8')
    print(f'Generated {len(critical.encode()):,} bytes of critical CSS; the complete stylesheet loads without blocking the first screen.')

if __name__=='__main__':
    main()
