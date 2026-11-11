The PMS site serves its fonts, icons, and responsive WebP images locally.

- `fonts/`: Latin subsets of Manrope and Plus Jakarta Sans for interface text, and DM Serif Display for editorial headlines, from Google Fonts. Each font's Open Font License is included alongside it. All fonts are served locally; no runtime Google Fonts request is needed.
- The 14 KB DM Serif Display file uses a generic English alphabet, digits and punctuation subset. Its optional loading strategy retains an elegant Georgia fallback when a connection is slow, preventing a late font swap from shifting the layout. Add glyph coverage if headings are translated beyond this character set.
- Inline SVG interface icons in `index.html` and `script.js`; the existing Lucide assets retain their license in `licenses/lucide-LICENSE`.
- `optimized/emerald.webp`: current hero artwork, served directly at its original resolution and quality on every screen. No saturation or brightness filter is applied; light, localized overlays preserve text contrast while keeping the emerald lighting vibrant. The previous supplied `Neon-hero.webp` remains available as source artwork.
- `patterns/emerald-flow.svg`: restrained ribbons and contour lines for the forest pricing section, echoing the supplied hero artwork. The SVG spans the section once without repeating; its matching neon mask uses the same dimensions and alignment so neither layer has tile seams. The other sections use distinct static lighting and architectural details instead of repeating the ribbon motif.
- `patterns/card-flow.svg`: a smaller ribbon motif for the pricing cards, paired with restrained green edge glows in CSS. Both pattern assets are local and have no text or external dependencies.
- `patterns/neon-wave-mask.svg`: follows the background ribbon paths. A composited transform moves the green light after content loads; off-screen layers are not rendered, and reduced-motion preferences keep the effect static.
- `patterns/contact-orbit-mask.svg`: a separate orbital pattern for Contact, with continuous arcs and a fine dotted orbit. Travelling emerald light uses a composited transform behind the content, stops rendering offscreen, and remains static with reduced motion.
- `illustrations/digital-studio.svg`: an original decorative illustration of layered black interface panels with mint accents. The services section displays it responsively; it is not presented as a portfolio project.
- The authentic PMS logo keeps its transparent artwork and is displayed on a black CSS background in the navigation and footer.
- The project screenshots retain 480px/960px variants selected through `srcset`; logos retain 72px/144px versions for display density. The original retired PNG/JPG exports can be recovered from Git history. Unused portraits and the old Anton font are not part of the website.

The PMS website uses the optimized copies. Preserve user-supplied artwork when regenerating assets.

- `icons/`: locally served technology symbols from [Devicon](https://github.com/devicons/devicon), including the Angular framework symbol. The Devicon license is retained in `licenses/devicon-LICENSE`. Monochrome Next.js and Express symbols are inverted on the dark banner; the other symbols retain their supplied colors. Two identical groups create a seamless loop. Reduced motion offers a stationary, manually scrollable row.
