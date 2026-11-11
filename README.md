# PMS Digital Solutions

## Production hosting

The PMS website is hosted on **Netlify** at [pmsdigitalsolutions.com](https://pmsdigitalsolutions.com), using the `main` branch of [Prince-Steele/PMS-Digital-Solutions](https://github.com/Prince-Steele/PMS-Digital-Solutions). Keep the existing Netlify project and domain connection.

The root `vercel.json` disables automatic Vercel Git deployments for the PMS website. The old Vercel project name `pm-digital-solutions` is not the production hosting target. Historical Vercel failures remain attached to their original commits. IslandTrail and Sterling are separate demo projects with their existing deployment settings.

## Projects

- The PMS Digital Solutions website is at the repository root.
- [IslandTrail Jamaica](travel-website/README.md) is a separate travel and tourism website concept. For a new Vercel project, import this same repository and set **Root Directory** to `travel-website`.
- [Sterling Advisory Group](professional-demo/README.md) is a static professional services website concept built with HTML, CSS, and JavaScript. For a separate static deployment, use `professional-demo` as the project root.

## PMS website development

The root website is plain HTML, CSS, and JavaScript; no build step is required. Serve it with `python -m http.server 4173 --bind 127.0.0.1` and open `http://127.0.0.1:4173`.

The single-page layout follows the supplied Figma Make design and the subsequent black, emerald, and white brand refinements. Pricing appears before the portfolio, and the desktop Services dropdown links directly to pricing; mobile navigation has six direct links, including Pricing, with no submenu. `style.css` is the single canonical stylesheet. After editing it, run `python scripts/build-critical-css.py` to refresh the generated first-screen styles embedded in `index.html`. This lets the first screen paint while the complete stylesheet loads. The previous services, portfolio, about, and contact URLs redirect to their corresponding sections.

The enquiry form validates required fields and prepares an email or WhatsApp draft containing the chosen service or package. The visitor reviews and sends it in their email app or WhatsApp. It does not claim that a message has been delivered. The existing Vercel contact API remains available in `api/contact.js`, but this design uses the reference's draft workflow.

Pricing defaults to JMD and offers a USD estimate view for both package categories and add-ons. The optional currency preference is stored locally in the visitor's browser. JMD prices remain canonical, including in quote prefills; USD estimates are rounded to whole dollars and retain their JMD basis in enquiries. The reference rate is **J$159.2806 per US$1**, the [Bank of Jamaica weighted average selling rate for 6 November 2026](https://egate.boj.org.jm/egate/Default.aspx). This dated preview rate is configured in `index.html` on `.currency-control`; update the rate, displayed date and reference together before publishing. No live exchange-rate request blocks page loading. Final currency and amount are confirmed in the quote.

Fonts, icons, artwork, and background patterns are served locally. The hero uses the supplied WebP at its original quality, and portfolio screenshots use responsive sources. Off-screen layout is deferred; scroll calculations are cached; background animation starts after the main content loads and runs only near the viewport. The pricing section's vector ribbons and aligned neon mask do not repeat into tiles. Assets are documented in [assets/README.md](assets/README.md).

The visual refinement uses the PMS palette: obsidian `#070C09`, forest `#123523`, emerald `#28C963`, mint `#A5EAB5` and white `#F7FAF7`. The authentic logo is shown at 56px on desktop and 44–48px on mobile, with a matching header/footer wordmark. Locally hosted DM Serif Display sets the main headlines; Manrope and Plus Jakarta Sans keep controls, body text and package details crisp. Services and Portfolio have light surfaces, Pricing uses forest green, About uses soft mint with a dark capabilities panel, and Contact uses obsidian with a light form. The existing hero artwork remains intact, with two small real-project previews on larger screens. Decorative motion respects reduced-motion preferences; mobile hides the additional hero previews, and Pricing retains travelling contour lights, while Contact has its own softly glowing orbital arcs. Both effects stop rendering offscreen and respect reduced-motion preferences.

To run the browser checks, install Playwright with `python -m pip install playwright`, then run `python tests/check-site.py`. Installed Google Chrome is required. The suite checks layouts from 320 to 1440 px, desktop dropdown and direct mobile navigation, service tabs, portfolio filters, both pricing categories, enquiry prefilling and validation, draft actions, and legacy redirects. Screenshots and results are written to `.local/design-checks`. It sends no messages.

Run `python scripts/measure-performance.py` to measure median FCP, LCP, layout shift, startup blocking time, TTFB, DOM readiness, and transfer size across three cold-cache runs. It includes local desktop and simulated mobile profiles (1.6 Mbps, 150 ms latency, 4x CPU slowdown). The test server compresses text with gzip. Reports are written to `.local/performance.json`. These are local lab measurements; production results depend on hosting, device, and connection quality.

The technology banner pairs local SVG symbols with technology names and a restrained emerald light sweep. Its two matching groups loop continuously, pause offscreen and on hover, and become a manually scrollable static row for reduced-motion visitors. The mobile menu uses direct links, scrolls internally on short screens, traps keyboard focus while open, and restores page access when closed or resized to desktop.
