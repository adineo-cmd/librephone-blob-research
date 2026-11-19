# Astro site — design (approved 2026-11-20)

## Intent
Replace the Python static generator with Astro as the deployed website, keeping
the same content and honesty rules. Update README and GitHub repo description
with the live website link.

## Goals
- Astro is what GitHub Pages deploys; `npm run build` produces `dist/`.
- Committed CSVs + Markdown remain the single source of truth.
- Preserve 245 devices, 9 families, three coverage states, 141 docs, 39 links,
  evidence-class badges, and the "device-reach not row-count" leverage ranking.
- Page count asserted at build (expected ~407, derived from actual data).
- README and GitHub repo description link to https://adineo-cmd.github.io/open-device/

## Non-goals
- No new research, no payload commits, no link-data invention.
- No deletion of the Python generator — it stays as provenance, not deployed.

## Constraints
- Astro 5, Node 24, static output.
- No new npm dependencies beyond Astro itself; CSV/Markdown parsing in-house.
- Deterministic output; facts-not-blobs; clean-room discipline unchanged.

## Approach chosen
Full port. `src/lib/data.ts` reads the committed CSVs/Markdown using Node `fs`
and a small dependency-free CSV parser. `src/lib/markdown.ts` renders the
measured Markdown subset with evidence-class badges. Astro pages under
`src/pages/` reproduce the Python site's routes. `src/layouts/Base.astro` and
`src/styles/site.css` carry the existing visual tokens. The Pages workflow runs
`npm ci && npm run build` and publishes `dist/`.

Alternatives rejected: Astro wrapping Python's `site/out` (not really a port);
full rewrite of content into MDX (would break the committed-CSV source of truth).

## Builder latitude
Exact component split, CSS organisation, and TypeScript types are the
implementer's call. Page routes and data semantics are fixed above.
