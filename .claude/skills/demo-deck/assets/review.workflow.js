// Adversarial review of a demo-deck script on three axes: facts, audience
// quality, TTS cleanliness. Run via the Workflow tool:
//   Workflow({ scriptPath: '<this file>', args: { deckDir, capturesDir } })
export const meta = {
  name: 'demo-deck-script-review',
  description: 'Adversarial review of a demo-deck narration.json on three axes',
  phases: [{ title: 'Review' }],
}

phase('Review')

const SCRIPT_PATH = `${args.deckDir}/narration.json`
const CAPTURES_DIR = `${args.capturesDir}/`

const FACT_PROMPT = `You are fact-checking a script for a demo video. Read ${SCRIPT_PATH} -- each
segment has a "narration" field (what gets spoken) and a "visual" field (what's shown).

Every factual claim, number, or figure in every "narration" string must be traceable to a real
file in ${CAPTURES_DIR} (real command output captured live, today) -- read the capture files
yourself and cross-check every number and claim against them.

Report: (a) any claim NOT backed by a real capture -- quote the narration line and say what's
unverifiable or wrong; (b) any number rounded, reframed, or stated in a misleading way even if
technically traceable (e.g. calling something "live" when its capture says otherwise); (c)
anything the captures clearly disprove. Be adversarial -- assume the scriptwriter wants to sound
better than reality and your job is to catch it. Quote exact narration text for every finding. If
a claim checks out, don't report it. Under 400 words.`

const QUALITY_PROMPT = `You are a skeptical viewer watching a demo video, hearing only the
"narration" fields of ${SCRIPT_PATH} read aloud in order (the "title"/"eyebrow" fields are
on-screen text, not spoken). Judge: (a) is there a moment you'd tune out -- jargon overload, a
beat that doesn't earn its place, a claim that sounds like spin; (b) does any honest limitation
or failure shown in the script land as a strength (evidence of rigor) or as a hedge that
undercuts confidence; (c) is the pacing right -- punchy short sentences, or does anything drag;
(d) what's the single weakest segment, and why. Quote narration text for every finding. Under 400
words.`

const TTS_PROMPT = `You are checking a script for TTS-cleanliness before it's fed to a
text-to-speech engine. Read ${SCRIPT_PATH} -- only the "narration" fields are spoken.

For every "narration" string, check: (a) any raw digit or symbol (£, %, etc.) that should be
spelled out as words for clean speech; (b) acronyms written with periods (e.g. "C.I.", "A.I.")
which risk the engine stuttering on each letter -- recommend the plain-caps form instead; (c) any
sentence over ~30 words, or a construction with nested dash-parentheticals around an internal
comma-list, that reads fine on the page but is hard to say aloud naturally -- recommend
simplifying; (d) word count per segment, flagging any segment far outside a natural spoken pace
(check this project's own measured rate empirically rather than assuming one, if any prior
duration data is available in the deck directory). Quote exact narration text for every finding.
Under 400 words.`

const [facts, quality, tts] = await parallel([
  () => agent(FACT_PROMPT, { label: 'fact-check', effort: 'high' }),
  () => agent(QUALITY_PROMPT, { label: 'audience-quality', effort: 'high' }),
  () => agent(TTS_PROMPT, { label: 'tts-cleanliness', effort: 'high' }),
])

return { facts, quality, tts }
