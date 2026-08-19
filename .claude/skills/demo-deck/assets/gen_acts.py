#!/usr/bin/env python3
"""Generate continuous-take audio for a narration.json script, split into
'acts' that each stay safely inside the TTS backend's hard duration ceiling.

Usage: python3 gen_acts.py <deck_dir> [--max-act-words N] [--verify]

Reads  <deck_dir>/narration.json  (list of {i, narration, eyebrow?, ...})
Writes <deck_dir>/acts.json       (the chosen split, reused by align_acts.py)
       <deck_dir>/audio/act<N>.wav

WHY ACTS EXIST, AND WHY THEY ARE THIS SIZE -- all measured, not guessed:

  The backend truncates at a hard ceiling of 163.84s of audio (a ~2048-token
  budget on a 12Hz codec). It does NOT error: it returns a shorter file and
  the tail of your script is silently missing. 552-word and 661-word inputs
  both produced exactly 163.8s, as did an earlier 1152-word one.

  Speaking rate is set by CONTENT, not by chance:
    - identical text re-run 3x varied only 5.4% (3.34-3.52 w/s)
    - different real acts varied 27%      (2.70-3.43 w/s)
  So a word budget that fits at 3.4 w/s can truncate at 2.7 w/s. The budget
  below is computed from the slowest rate ever observed, not the average.

    163.8s ceiling x 2.70 w/s (slowest) = 442 words absolute
    default 350 words = ~130s at the slowest rate = 79% of the ceiling

  Prefer FEWER, LONGER acts. Each act is a separate generation, so each seam
  is a chance for pace and tone to shift; 5 acts sound more of a piece than
  12. Push act size up to the safe budget rather than down.
"""
import json, pathlib, subprocess, sys, time, math, argparse, requests

TTS = 'http://localhost:7693'
VOICE = 'andy3'

# --- measured constants (see module docstring) -------------------------------
HARD_CEILING_S = 163.84   # backend truncates here, silently
TRUNCATION_S = 163.0      # any act at/above this almost certainly lost its tail
SLOWEST_RATE_WPS = 2.70   # slowest rate observed on real narration content
DEFAULT_MAX_ACT_WORDS = 350
ABSOLUTE_MAX_ACT_WORDS = 420  # ~95% of ceiling at the slowest rate: too tight


def synth(text):
    last = None
    for attempt in range(5):
        try:
            r = requests.post(f'{TTS}/api/qwen3/generate',
                              json={'text': text, 'mode': 'clone', 'voice_name': VOICE},
                              timeout=900)
            r.raise_for_status()
            return requests.get(f"{TTS}{r.json()['audio_url']}", timeout=900).content
        except Exception as e:
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


def dur(path):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=nk=1:nw=1', str(path)], capture_output=True, text=True)
    return float(o.stdout.strip())


def words_of(seg):
    return len(seg['narration'].split())


def chunk_into_acts(narr, max_words):
    """Split into the FEWEST acts that respect max_words, balanced in size,
    with boundaries snapped to topic changes.

    Three properties, in priority order:
      1. no act exceeds max_words (correctness -- avoids truncation)
      2. as few acts as possible   (fewer seams -> steadier tone)
      3. boundaries land where the narrative already turns, so any small pace
         shift coincides with a topic change and reads as deliberate
    """
    total = sum(words_of(s) for s in narr)
    n_acts = max(1, math.ceil(total / max_words))

    # Grow the act count until an even split actually fits under the cap.
    while True:
        target = total / n_acts
        boundaries = _split_at(narr, n_acts, target, max_words)
        if boundaries is not None:
            return boundaries
        n_acts += 1


def _topic_changes(narr):
    """Indices where a new topic starts -- an eyebrow change is this project's
    own marker for 'new beat'. Falls back to empty, which just means boundaries
    are chosen purely on balance."""
    marks = set()
    prev = None
    for pos, seg in enumerate(narr):
        eb = (seg.get('eyebrow') or '').strip().lower()
        if eb and prev is not None and eb != prev:
            marks.add(pos)
        if eb:
            prev = eb
    return marks


def _split_at(narr, n_acts, target, max_words):
    marks = _topic_changes(narr)
    acts, current, current_words, made = [], [], 0, 0

    for pos, seg in enumerate(narr):
        w = words_of(seg)
        if w > max_words:
            # A single segment over budget can't be split here -- the script
            # itself needs shortening. Surface it rather than truncate later.
            raise SystemExit(
                f'segment {seg["i"]} is {w} words, over the {max_words}-word act budget. '
                f'Split it into two segments in narration.json.')

        remaining_acts = n_acts - made
        would_exceed = current_words + w > max_words
        # Close the act if we must, or if we're at/past target AND this is a
        # topic change (a natural place for a seam), leaving room for the rest.
        at_target = current_words >= target * 0.75
        natural = pos in marks
        must_close = would_exceed
        want_close = current and at_target and natural and remaining_acts > 1

        if must_close or want_close:
            if not current:
                return None
            acts.append(current)
            made += 1
            current, current_words = [], 0

        current.append(seg['i'])
        current_words += w

    if current:
        acts.append(current)
    # Reject a split that overshot the intended act count badly (caller retries
    # with more acts), or that left an act over budget.
    if any(sum(words_of(s) for s in narr if s['i'] in a) > max_words for a in acts):
        return None
    return acts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck_dir')
    ap.add_argument('--max-act-words', type=int, default=DEFAULT_MAX_ACT_WORDS)
    ap.add_argument('--verify', action='store_true',
                    help='transcribe each act and confirm its final words survived')
    args = ap.parse_args()

    if args.max_act_words > ABSOLUTE_MAX_ACT_WORDS:
        raise SystemExit(
            f'--max-act-words {args.max_act_words} exceeds the safe ceiling of '
            f'{ABSOLUTE_MAX_ACT_WORDS}. At the slowest observed rate '
            f'({SLOWEST_RATE_WPS} w/s) that is {args.max_act_words / SLOWEST_RATE_WPS:.0f}s, '
            f'past the {HARD_CEILING_S}s truncation ceiling.')

    here = pathlib.Path(args.deck_dir)
    narr = json.loads((here / 'narration.json').read_text())
    by_i = {seg['i']: seg for seg in narr}

    acts = chunk_into_acts(narr, args.max_act_words)
    (here / 'acts.json').write_text(json.dumps(acts, indent=2))

    total_words = sum(words_of(s) for s in narr)
    print(f'{len(narr)} segments, {total_words} words -> {len(acts)} acts '
          f'(cap {args.max_act_words} w/act)')

    aud_dir = here / 'audio'
    aud_dir.mkdir(exist_ok=True)
    total, truncated = 0.0, []
    for act_i, idxs in enumerate(acts):
        text = ' '.join(by_i[i]['narration'] for i in idxs)
        wc = len(text.split())
        worst = wc / SLOWEST_RATE_WPS
        flag = '  <-- tight' if worst > HARD_CEILING_S * 0.9 else ''
        print(f'act {act_i} (segments {idxs[0]}-{idxs[-1]}): {wc}w, '
              f'worst-case {worst:.0f}s{flag}')
        audio = synth(text)
        wav = aud_dir / f'act{act_i}.wav'
        wav.write_bytes(audio)
        d = dur(wav)
        total += d
        rate = wc / d if d else 0
        warn = ''
        if d >= TRUNCATION_S:
            warn = '  *** TRUNCATED: hit the backend ceiling, tail is missing ***'
            truncated.append(act_i)
        print(f'  {d:.1f}s  {rate:.2f} w/s{warn}')
        time.sleep(0.3)

    if args.verify:
        _verify_tails(here, acts, by_i, truncated)

    print(f'\nTOTAL: {total:.1f}s -> {int(total // 60)}:{total % 60:04.1f}')
    if truncated:
        raise SystemExit(
            f'\nacts {truncated} hit the {HARD_CEILING_S}s ceiling and lost their tails. '
            f'Re-run with a smaller --max-act-words, or shorten those segments.')
    print('Next: python3 align_acts.py', args.deck_dir)


def _norm_tokens(text):
    import re
    return [t for t in (re.sub(r"[^a-z0-9']", '', w.lower()) for w in text.split()) if t]


def _verify_tails(here, acts, by_i, truncated):
    """Belt-and-braces: transcribe each act and confirm its closing words
    actually made it into the audio. Catches a truncation that landed just
    under the duration threshold.

    Matching is FUZZY on purpose. The transcriber mishears homophones
    ('seam' -> 'scene'), so an exact substring test produces false alarms on
    perfectly good audio. Compare the last N tokens as a sequence and accept a
    high-similarity match instead.
    """
    import difflib
    TAIL_N = 8
    THRESHOLD = 0.6
    print('\nverifying act tails against the script...')
    for act_i, idxs in enumerate(acts):
        wav = here / 'audio' / f'act{act_i}.wav'
        jp = here / f'_verify_act{act_i}.json'
        subprocess.run(['mw', 'transcribe', '--format', 'json', str(wav),
                        '-o', str(jp), '--overwrite'], check=True, capture_output=True)
        heard = ' '.join(s['text'] for s in json.loads(jp.read_text())['segments'])
        jp.unlink(missing_ok=True)

        want = _norm_tokens(by_i[idxs[-1]]['narration'])[-TAIL_N:]
        got_tail = _norm_tokens(heard)[-(TAIL_N * 3):]  # window, not the whole transcript
        # Coverage of the WANTED tokens, not SequenceMatcher.ratio(): ratio is
        # 2*M/(len(a)+len(b)), so an 8-token tail against a 24-token window
        # caps at 0.5 even on a perfect match. Fraction-matched has no such
        # length bias.
        if want:
            sm = difflib.SequenceMatcher(None, want, got_tail, autojunk=False)
            matched = sum(b.size for b in sm.get_matching_blocks())
            ratio = matched / len(want)
        else:
            ratio = 1.0
        # A tail that survived scores high even with a mis-heard word or two.
        ok = ratio >= THRESHOLD
        verdict = 'present' if ok else 'MISSING -- likely truncated'
        print(f"  act {act_i}: tail {verdict} (similarity {ratio:.2f}, wanted {' '.join(want)!r})")
        if not ok and act_i not in truncated:
            truncated.append(act_i)


if __name__ == '__main__':
    main()
