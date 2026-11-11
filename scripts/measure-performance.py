"""Measure cold-cache browser paints locally. Requires Playwright and Chrome.

Usage: python scripts/measure-performance.py
Mobile profile: 390x844 at 1.6 Mbps, 150 ms latency, 4x CPU slowdown.
The local server uses gzip for text, as a production static host typically does.
These lab measurements do not predict real-user network/server latency.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import median
from threading import Thread
import gzip
import io
import json
import mimetypes

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class CompressedHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_file() and path.suffix in {".html", ".css", ".js", ".svg"} and "gzip" in self.headers.get("Accept-Encoding", ""):
            body = gzip.compress(path.read_bytes())
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return io.BytesIO(body)
        return super().send_head()


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(CompressedHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            for mobile in (False, True):
                for name in ("index",):
                    runs = []
                    for _ in range(3):
                        context = browser.new_context(viewport={"width": 390 if mobile else 1440, "height": 844 if mobile else 900}, device_scale_factor=1)
                        page = context.new_page()
                        page.add_init_script("""window.paintMetrics = {lcp:0, cls:0, tbt:0};
                          new PerformanceObserver(l => {window.paintMetrics.lcp=l.getEntries().at(-1).startTime}).observe({type:'largest-contentful-paint',buffered:true});
                          new PerformanceObserver(l => {for(const e of l.getEntries()) if(!e.hadRecentInput) window.paintMetrics.cls+=e.value}).observe({type:'layout-shift',buffered:true});
                          new PerformanceObserver(l => {for(const e of l.getEntries()) window.paintMetrics.tbt+=Math.max(0,e.duration-50)}).observe({type:'longtask',buffered:true});""")
                        client = context.new_cdp_session(page)
                        client.send("Network.enable")
                        client.send("Network.setCacheDisabled", {"cacheDisabled": True})
                        if mobile:
                            client.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1600000 / 8, "uploadThroughput": 750000 / 8})
                            client.send("Emulation.setCPUThrottlingRate", {"rate": 4})
                        page.goto(f"http://127.0.0.1:{server.server_port}/{name}.html", wait_until="networkidle")
                        page.evaluate("document.fonts.ready")
                        page.evaluate("new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))")
                        runs.append(page.evaluate("""() => {
                          const nav=performance.getEntriesByType('navigation')[0];
                          return {fcp:performance.getEntriesByName('first-contentful-paint')[0].startTime,lcp:window.paintMetrics.lcp,cls:window.paintMetrics.cls,tbt:window.paintMetrics.tbt,ttfb:nav.responseStart,dom_ready:nav.domContentLoadedEventEnd,bytes:performance.getEntriesByType('resource').reduce((n,r)=>n+r.encodedBodySize,0),total_bytes:nav.encodedBodySize+performance.getEntriesByType('resource').reduce((n,r)=>n+r.encodedBodySize,0)};
                        }"""))
                        context.close()
                    result = {"profile": "simulated-mobile" if mobile else "local-desktop", "page": name, **{key: round(median(r[key] for r in runs), 3) for key in runs[0]}}
                    results.append(result)
                    print(json.dumps(result), flush=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    output = ROOT / ".local/performance.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
