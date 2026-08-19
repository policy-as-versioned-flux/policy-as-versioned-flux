# Wardley maps in mermaid — verified syntax

Mermaid **11.15.0** (the version `mmdc` resolves to here) ships a native Wardley
renderer. Everything below was verified empirically against that version by
rendering it; anything that failed to render is listed under *Not supported* so
you don't burn time rediscovering it. Re-verify against `mmdc --version` if the
toolchain has moved.

Render exactly like any other diagram in this pipeline:

```sh
mmdc -i map.mmd -o mermaid/map.png -b transparent -w 1600 -H 1000 \
  -c assets/mermaid-theme.json -p assets/mermaid-puppeteer-config.json
```

## Working syntax

```
wardley-beta
  title Governance tooling landscape
  evolution genesis -> custom built -> product -> commodity

  anchor Board [0.95, 0.62]
  component Priced risk [0.80, 0.28]
  component Policy engine [0.62, 0.70] (buy)
  component Manual audit [0.55, 0.18] inertia
  component Labelled thing [0.40, 0.40] label [12, -18]

  Board -> Priced risk
  Priced risk -> Policy engine ;proportionate to the £
  Policy engine --> Reconciliation
  Signed feeds -.-> Policy engine

  evolve Manual audit 0.72

  note "everything right of here is commodity" [0.12, 0.80]
  annotations [0.03, 0.02]
  annotation 1,[0.55,0.35] "audit displaced by continuous evidence"

  accelerator Market pull [0.40, 0.55]
  deaccelerator Inertia drag [0.30, 0.35]
  size [1400, 900]
```

**Coordinates are `[visibility, evolution]`** — visibility `0` bottom to `1`
top (how visible to the user), evolution `0` genesis (left) to `1` commodity
(right). This is the standard Wardley pair order; getting it backwards is the
usual first mistake.

| Statement | Form | Notes |
|---|---|---|
| diagram | `wardley-beta` | the opening keyword |
| title | `title Some Title` | |
| axis stages | `evolution a -> b -> c -> d` | renames the x-axis bands; any number of stages |
| anchor | `anchor Name [vis, evo]` | the user need |
| component | `component Name [vis, evo]` | multi-word names are fine, unquoted |
| strategy | `component N [v, e] (build)` | `build` \| `buy` \| `outsource` \| `market` |
| inertia | `component N [v, e] inertia` | draws the resistance bar |
| label nudge | `component N [v, e] label [x, y]` | pixel offset, negatives allowed |
| link | `A -> B` | also `-->`, `-.->`, `>` |
| link label | `A -> B ;text here` | **leading `;`** starts the label |
| movement | `evolve Name 0.72` | red dashed arrow to the target evolution |
| note | `note "text" [vis, evo]` | **text must be quoted** |
| annotation | `annotation 1,[0.55,0.35] "text"` | **comma after the number**; text quoted |
| annotation box | `annotations [x, y]` | where the numbered list is drawn |
| accelerator | `accelerator Name [vis, evo]` | also `deaccelerator` |
| canvas | `size [1400, 900]` | see sizing below |

Numbers need a decimal point (`0.8`, not `.8` and not `8`) — the grammar's
number terminal is `[0-9]+\.[0-9]+`. The annotation *index* is a plain integer.

## Gotchas found by rendering

- **The `wardley` config block is inert.** Setting `wardley: {labelFontSize,
  nodeRadius, padding, showGrid, ...}` in the mermaid config JSON changes
  nothing — verified by rendering with deliberately extreme values and getting
  byte-identical output. Size the map with the in-diagram `size [w, h]`
  statement (which does work) and `mmdc -w/-H`, not with config.
- **The annotations box renders light-on-light** against this deck's dark
  theme — a near-white panel with pale text, effectively unreadable on a slide.
  Prefer `note "..."`, which renders as bold light text and reads cleanly. Use
  `annotation` only if you've checked the rendered PNG and are happy with it.
- **Keep the top-most component at visibility ≤ 0.90.** At `0.95` the label
  collides with the plot's top edge and clips.
- **A single coordinate pair per annotation.** The multi-pair OWM form
  (`annotation 2,[[..],[..]] "text"`) is rejected by this version.
- **Pipelines need braces:**
  ```
  pipeline Parent {
    component Child [0.3]
  }
  ```
  A pipeline child takes evolution only (one number), not a coordinate pair.

## Not supported in 11.15.0

`.8`-style bare-decimal coordinates · multi-coordinate annotations · the
`wardley` config block · unquoted `note`/`annotation` text.

## Using it on a slide

Render to PNG and reference it exactly like any other diagram —
`<img class="diagram" src="mermaid/map.png">`. A Wardley map is dense; give it
a slide of its own and let the narration walk one movement, not five. The
strongest use is a *movement* claim (`evolve`), because that's the argument the
audience can't get from a static architecture diagram.
