# Sinkronized · UI design direction

## Reference language

This project uses design principles observed in two public references, **not** their proprietary assets, source code, branding, or exact font files.

- [House of Giants](https://houseofgiants.com/) — confident, direct headline hierarchy, readable paragraph measure, simple navigation, purposeful emphasis.
- [Apple Ads](https://ads.apple.com/) — consistent modular tile grids, clear alignment across cards, generous negative space, predictable buttons and section rhythm.

The brand remains **Sinkronized**, with the existing Arizona logo, original Sonoran Sand palette, research language, and provenance.

## Where the system lives

- `web/design-system.css`: unified presentation and responsive rules. It loads **after** `styles.css` and `map.css` to provide one intentional design layer.
- `web/index.html`: semantic sections, navigation, research and field atlas.
- `web/app.js`: source-driven hotspot list, time chart, synchronization with map and study report. **Do not hardcode region names or measurements.**
- `web/motion.js`: decorative contour animation; respects reduced motion. It must not animate or change map science.
- `web/build-preview.mjs`: embeds the same source CSS and JS into `web/preview.html`. The portable preview's tile/image dependencies differ from a fully served site.

## Typographic scale (responsive)

| Element | Target CSS | Why |
| --- | --- | --- |
| Typeface | System sans: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Arial | Robust, crisp, no license-dependent downloads |
| Brand wordmark | 24px, weight 750 | Clear but not dominant |
| Navigation | 12–13px, weight 600–700 | Compact but readable |
| Hero primary line | 45–68px, weight 750; 42–56px on mobile | Confident display hierarchy |
| Hero second line | 30–43px, weight 470 | Support headline rather than compete |
| Hero introduction | 18–21px, weight 500 | Laptop-readable |
| Body copy | 16–17px, line-height 1.65–1.76 | Comfortable reading measure |
| Section headings | 32–49px, weight ~730 | Distinguish major sections |
| Card headings | 19–27px, weight ~690–700 | Align across equal-height cards |
| Eyebrows and metadata | 11–12px, weight 750 | Secondary, not microtext |

## Grid and interaction rules

- Content width: `1360px` maximum for editorial sections; outer gutters `clamp(20px,4.3vw,72px)`.
- Cards use a consistent `18px` corner radius, light borders, limited shadows and aligned top headings.
- Three-across editorial cards reflow to one column on smaller screens. Never overflow paragraphs or cut off scientific source links.
- Primary CTA: dark ink fill, `13px` radius, `15px` readable label. Secondary CTA is simple underlined text.
- Navigation is restrained and sticky on desktop; mobile navigation wraps.
- Atlas stays **map-first**. Region names always come from the team’s `hotspots.geojson`. On selection, the authentic interactive chart appears with the map, and the detailed report is directly below for scrolling.
- Do not substitute decorative placeholder graphs for measured exports, or reinterpret a radar line-of-sight measurement as vertical ground motion without justification.
- Terrain and satellite basemaps and the current study overlays are unchanged.
- `prefers-reduced-motion: reduce` must preserve legibility and remove decorative animation.

## Review checklist

1. At typical 13–15-inch laptop widths, inspect the hero, navigation wrap, equal card alignment, map overlays and scroll-to-report flow.
2. At tablet and phone widths, check tiles, region selector, map height, graph accessibility and expandable measurement notes.
3. Compare graph dates with the map's cumulative frame date after hover, click/pin, play and reset.
4. Check source links, links to resources, and text/controls over the muted desert artwork.
5. Refresh `web/preview.html` using `node web/build-preview.mjs` after source changes.

**Deployment:** The original repository's `main` does not automatically deploy the public Vercel site; it is connected to teammate's `ray021207/NASA-Hackathon` fork. A teammate with fork write access must sync that fork's `main`.
