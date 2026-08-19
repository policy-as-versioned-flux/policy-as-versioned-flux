---
name: demo-deck
description: Build a narrated demo video of this project's current real, running state
disable-model-invocation: true
---

# demo-deck

Produces a narrated video demo (voice + slides) of something real and currently working in this
repo — grounded entirely in evidence captured live, this run. Not a pitch, not a fundraising ask
unless the user explicitly asks for one: a demo. Assets referenced below live in `assets/`
alongside this file.

**The cold-start rule.** Every fact, number, screenshot, and script line must come from a command
you ran *this run*. Never copy a number, capture file, or line of narration from a previous
`demo-v*` directory — code and claims move fast here, and a stale figure is worse than a missing
one. The previous deck's own `assets/*.py`/`.sh`/`.js` pipeline tooling is fair to reuse unchanged
(that's what `assets/` in this skill already is); its *content* is not.

## 0. Subject and length

Ask the user (do not assume): which subject to demo — this repo has more than one live subsystem
(check `estate/`, `twin/`, and any other top-level project directories for what currently exists —
don't hardcode a guess), and what target length. Default to ~7-10 minutes if the user has no
preference; Pecha-Kucha-style pacing (short, punchy segments, slide changes driven by the script's
own rhythm, not a fixed timer) works well but isn't mandatory — ask if unsure.

Done when: a subject and a target length (or an explicit "you decide") are confirmed.

## 1. Discover

Find the subject's current real proof surface: verify/demo scripts, a `verify-all`-style gate if
one exists, capability/grade tracking files, recent build-ticket status, README/runbook docs that
describe what's live vs narrated/stubbed. Read the subject's own docs first — they usually say
which claims are safe to demonstrate live already (an `[LIVE]`/`[NARRATED]` tag, a depth-grade
file, a `does-not-do` register) and often draft a longer-form narrative to compress from.

Note anything with a *visual* surface too — a dashboard, a rendered report, a repo page, a running
UI — since those become screenshot slides rather than terminal slides.

Done when: you have a concrete list of real, currently-existing commands you could run to
demonstrate this subject, and you know which ones are honestly narrated-only right now (say so
plainly in the script later — don't paper over a gap).

## 2. Capture

Run every command from step 1 that is **safe**: read-only or acting only on disposable local state
(a local cluster's already-applied config, a local git worktree). Save each command's real,
complete output to a fresh `captures/` directory under this run's deck directory (see Output
location below) — verbatim, including a real failure if one occurs. An honest red result is
material, not a bug to hide.

**Never run**, even if a discovered script offers to: anything that pushes, opens a PR or issue,
sends a signed commit, deletes or resets a cluster/namespace, or mutates any shared/remote state.
Read the script first if its safety isn't obvious from its name; if it's genuinely side-effecting,
capture what it *would* do (dry-run flag, or just quote the relevant code) and note in the script
later that it wasn't executed live, and why.

### Web screenshots

If the subject has a UI, dashboard, repository page, or rendered artefact worth showing, capture it
now into `captures/shots/`:

- **Public or local URL** (a local Grafana, a docs page, a rendered HTML report, a GitHub page):
  `node assets/screenshot.js <url> captures/shots/<name>.png --width 1600 --height 1000` — add
  `--wait <selector>` for a JS-rendered page, `--full` for the whole scrollable page, `--dark` to
  request the site's dark theme so it sits better on a dark slide.
- **Behind a login** (an authenticated dashboard, a private console): the headless helper has no
  session, so drive the user's own logged-in browser with the claude-in-chrome MCP tools instead.
  Load them in one call — `ToolSearch` with
  `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp`
  — then open a new tab, navigate, and screenshot. Ask the user before opening anything that needs
  their session.

Done when: every safe command from step 1 has a real output file, every skipped command has a
one-line reason recorded, and every screenshot the plan needs exists as a real PNG under
`captures/shots/`.

## 3. Plan

Draft a beat list sized to the target length, each beat citing the specific capture(s) that back
it. Don't force a fixed slide count — let genuinely distinct beats be genuinely distinct slides,
and let one beat span two slides (e.g. a setup + a payoff) when that's clearer than cramming. If a
subject has a mechanism that senses/reasons/acts/learns autonomously (an agent loop, not just a
static check), that usually deserves to be the weighted centre of the demo, not one beat among
many — ask the user if you're unsure which part matters most to them.

Done when: every planned beat names its evidence source and there is no beat without one.

## 4. Script

Write `narration.json` — a list of `{i, eyebrow, title, narration, visual}`. `narration` is the
only field spoken aloud; `title`/`eyebrow` are on-screen text and can carry symbols/digits freely.
`visual` names the slide type and which capture, screenshot, or diagram it renders — see
`assets/demo-deck-scaffold.html` for every component's markup:

| type | use it for |
|---|---|
| `terminal` | real captured command output — the workhorse; most slides should be this |
| `screenshot` | a real page captured this run, in a browser frame (or `fullbleed`, unframed) |
| `mermaid` | a flow/sequence/architecture diagram of a real mechanism |
| `wardley` | evolution and **movement** of a landscape — read `assets/wardley-reference.md` first |
| `table` | a comparison where the rows are the argument |
| `mockup` | stat cards, a ledger line, a checklist — for a number that has no terminal |
| `news` | the consequence a risk buys, as a headline — see the integrity rule below |
| `meme` | one reject/prefer contrast, built in plain CSS, never a fetched image |
| `title` | hook, thesis, close |

Keep the ratio honest: evidence types (`terminal`, `screenshot`, `wardley`, `mermaid`, `table`)
should dominate; `title`/`mockup`/`meme`/`news` are seasoning.

**Integrity rule for `news` and `meme` slides.** These invent content, so they carry a hard
constraint: never use a real publication's name, masthead, branding, or byline, and never present
an invented quote, post, or story as something that happened. Use an obviously invented outlet
name, and keep the `.hypothetical` banner on the slide. A headline mockup is a legitimate way to
make a priced risk concrete — *"this is the headline this £ figure is buying insurance against"* —
and it stays legitimate exactly as long as no frame of it could be screenshotted and mistaken for
a real report. The same goes for a social-post mockup: invented handle, labelled illustrative.

TTS-clean the `narration` text as you write it, not as a later pass:
- Spell out every number and currency figure as words. No raw digits, `£`, or `%` in `narration`.
- Acronyms as plain caps (`CI`, `AI`), never dotted (`C.I.`) — dots risk a stutter between letters.
- Avoid a dash-set-off aside that itself contains a comma list; split into two sentences instead.
- Keep most segments under ~30 words; let a genuinely important beat run longer rather than
  padding a thin one.

Done when: every `narration` string traces to a named capture (or is explicit, honest
narration-only framing), and none of the formatting rules above are violated.

## 5. Adversarial review

Run `assets/review.workflow.js` via the Workflow tool, passing `args: { deckDir, capturesDir }`.
Three parallel agents check facts (against the captures only), audience quality, and TTS
cleanliness. Read every finding; fix what's real, and if you deliberately leave something
unchanged, know why. Re-run after material edits.

Done when: no open fact-check finding remains unaddressed.

## 6. Build the deck

Copy `assets/demo-deck-scaffold.html` to `<deck_dir>/deck.html` and author one real `.slide` div
per `narration.json` entry (`data-i` matching `i`), replacing the scaffold's example slides —
never leave a placeholder in the shipped deck.

For a `mermaid` or `wardley` visual, write a `.mmd` file and render it to PNG:

```sh
mmdc -i x.mmd -o mermaid/x.png -b transparent -w 1400 -H 900 \
  -c assets/mermaid-theme.json -p assets/mermaid-puppeteer-config.json
```

Wardley maps are native in the mermaid version here (`wardley-beta`), but the syntax has real
traps and several statements that silently fail — **read `assets/wardley-reference.md` before
writing one**; it carries the verified grammar and the rendering gotchas.

Copy captured screenshots into `<deck_dir>/shots/` and reference them from the browser-frame
markup, putting the genuine captured URL in the `.urlbar`.

Done when: every segment has a corresponding slide with real content, and every diagram and
screenshot referenced actually exists on disk.

## 7. Generate audio

`python3 assets/gen_acts.py <deck_dir>`. This chunks the script into "acts" (~220 words each by
default) and generates one continuous TTS take per act — see **TTS pipeline notes** below for why
it's chunked rather than one giant call, and why acts rather than one clip per segment.

Check the total against the step-0 target. If it's off by more than about 10%, revise
`narration.json` (cut or add real content — never pad with filler) and re-run this step; the
regenerated acts will naturally reflect the edit. This is the length-check loop — iterate here,
not by force-trimming audio afterward.

Done when: total duration is within the target range.

## 8. Align

`python3 assets/align_acts.py <deck_dir>`. Force-aligns each act's audio to its known text via
`mw` (MacWhisper CLI) plus sequence matching, producing `segment_timing.json` — the real per-word
timestamp each segment starts at, so slide changes land on the words rather than an estimate.
Watch for its own low-match-rate warnings per act.

Done when: `segment_timing.json` exists with no unresolved low-match-rate warning, or any warning
has been spot-checked (see step 10) and found acceptable.

## 9. Render slides

`node assets/render.js <deck_dir>` — screenshots every slide to `<deck_dir>/slides/sNN.png`.

Then **look at the rendered PNGs** — at minimum every text-heavy terminal slide, every diagram, and
every screenshot slide. The deck is a fixed 1920×1080 with no scrollbar, so content that overflows
is silently cropped: a long capture runs off the bottom, a wide one clips at the right, a Wardley
label collides with the plot edge. None of this is visible in the HTML source, only in the render.
Trim the pasted output or drop the font size (`.tbody.small`) and re-render until each slide fits.

Done when: one PNG exists per segment, and every one you have inspected fits inside the frame.

## 10. Assemble

`assets/assemble.sh <deck_dir>` — builds `<deck_dir>/output.mp4`: one continuous audio track,
each slide held for its real force-aligned duration.

Then spot-check: pull frames at three or more distinct, spread-out timestamps
(`ffmpeg -ss <t> -i output.mp4 -frames:v 1 out.png`) and confirm each shows the slide its
`segment_timing.json` start time says it should. This is cheap and catches an alignment mismatch
before delivery, not after.

Done when: every spot-checked frame matches its expected segment.

## 11. Deliver

Send `output.mp4` to the user (`SendUserFile`). Say what's actually new or different from any
prior version by content, not just by file path — the cold-start rule means this run's numbers may
differ from last time's even for the "same" subject, and that's worth naming, not hiding.

## Output location

A fresh, numbered directory per run — never overwrite a previous one. Scan the subject's own
`.scratch/<subject>/` (or wherever this repo keeps that subject's scratch work) for existing
`demo-v*` directories and use the next number. If no such convention exists yet for this subject,
create `.scratch/<subject-slug>/demo-v1/` and start the convention.

## TTS pipeline notes (reference)

- **Voice**: `tts.py --help` documents the CLI, but its stdin-detection has a bug under a
  non-interactive shell (it prefers an empty stdin over the text argument, silently sending empty
  text and getting a 400). `assets/gen_acts.py` calls the API directly
  (`POST /api/qwen3/generate`, `{"text","mode":"clone","voice_name":"andy3"}`) and sidesteps this
  entirely — prefer that over shelling out to `tts.py` in a script.
- **Generation length cap**: a single call over roughly 550-600 words was observed to truncate
  silently and reproducibly (identical cutoff point on repeat runs with memory freed in between —
  a backend generation-length cap, not a resource issue). `gen_acts.py`'s ~220-word default act
  size leaves a large safety margin.
- **`/api/tts/align-words`** (the TTS server's own forced-alignment endpoint) returned 503 on every
  call across two independent full runs. Don't depend on it; `align_acts.py` uses `mw` instead,
  which is a real, separately-verified-working local tool (`mw transcribe --format json` gives
  word-level timestamps).
- **ffmpeg concat** needs absolute paths in the list file (paths resolve relative to the list
  file's own location, not your cwd) — both `gen_acts.py`/`assemble.sh` already handle this.
- **`-vsync vfr` and `-r`/`fps` together** is a contradictory ffmpeg argument pair; `assemble.sh`
  uses `fps=30` inside `-vf` instead, which coexists fine with the concat demuxer's per-image
  `duration` directive.
- If a TTS call fails oddly (400/503/timeout) and nothing else has changed, check system memory
  before assuming a code bug — the local backend is memory-sensitive.
