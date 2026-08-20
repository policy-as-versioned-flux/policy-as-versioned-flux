# Pitch v4 — script (draft 1)

**To:** Andy, CEO of Control Plane. **Target:** 6:40 (400s ± 10s). **Voice:** Qwen3 clone `andy3`
via `tts.py`, non-interactive form: `echo "line" | python3 tts.py > out.wav`. TTS-clean: numbers
spelled out, minimal jargon, natural spoken cadence, contractions where they'd actually be said.

Every fact below is sourced from live command output captured today — see
`.scratch/talk-spec/pitch-v4/captures/`. Nothing is carried forward from pitch-v3 or the `demo/`
draft.

---

### S1 — HOOK · what does a breach actually cost? [real terminal: fair.py summary]
> What does a breach actually cost you? Not a red, amber, green light — a number, in pounds. Here's ours, computed live, right now: thirty four thousand, nine hundred and fifty eight pounds. That's not the average year. That's the bad one. The one your board should be provisioning for.

### S2 — THESIS · governance is a priced judgement [graphic: the binary lie]
> Most governance tooling gives you a tick. Compliant, or not — a binary that prices nothing. We built the opposite bet: governance as a priced, versioned, continuously re-tuned judgement. Not a checkbox. A number that moves, because the world moves.

### S3 — PROOF OF LIFE · not slideware [real terminal: kind get clusters, kubectl get nodes]
> And here's the difference from every deck you've sat through: none of this is illustration. Three real Kubernetes clusters, up right now. Real signed commits. A real repository you can clone tonight. Everything I show you for the next six minutes, I can run again in front of you.

### S4 — THE MONEY SHOT, SET UP · one control, three institutions [built table]
> Now watch the moment that actually sells this. One shared platform. Three institutions on it — an e-commerce retailer, a fintech, and a health provider. Same engine, same rule, running on all three: encrypt data at rest.

### S5 — THE MONEY SHOT, PAYOFF · same control, opposite verdicts [real terminal + table]
> Identical control. Identical risk bought — twenty one thousand, one hundred and seven pounds, on every single cluster. Watch what happens. For the retailer, that's under budget: it audits. For the fintech and the hospital, it blows the budget: it blocks. Same rule. Opposite verdict. Because the pounds say so — not a policy author's opinion.

### S6 — NOT A CLIFF EDGE · graded response [graphic: tier spectrum]
> And it's never just yes or no. Fall behind on patching, your workload doesn't get killed — it gets caged. Throttled, sandboxed, watched, more expensive to keep running. A spectrum of consequence, proven on a real cluster, not a pass-fail cliff edge.

### S7 — THE ECONOMICS · total cost of risk [built stat block]
> That cage costs real money, while the risk it's containing still sits there. Add both up — the risk you're keeping, plus the cost of every control holding it — and you get one number: total cost of risk. And it proves, provably, that staying current is the cheap path.

### S8 — THE MATHS IS REAL · the engine self-checks [real terminal: fair.py selfcheck]
> These pounds aren't guesses. Calibrated estimates, a Monte Carlo simulation, and the tail your insurer actually prices — the same maths Solvency Two uses. Here's the engine checking its own arithmetic, live, and passing. Change one input, and the number moves in front of you.

### S9 — EXEMPTIONS, DISSOLVED · no more favours [real terminal: verify-conditional/exemption]
> We killed the ugliest word in governance: exemption. No back-channel favours. Instead — you may do this, if you meet these conditions. Versioned, uniform, priced. Anyone who meets the conditions gets the same treatment an executive would have to ask for specially.

### S10 — THE LIVING LOOP · it war-games itself [mermaid: feeds → war-gamer → signed PR → human → merge]
> Then it comes alive. Real threat feeds, new vulnerabilities, regulator fines — all pouring in. An agent stress-tests every control and asks: is this still proportionate, or did the world just move? When it drifts, the agent does exactly one thing: it opens a pull request. It proposes. It never disposes. A human and a gate decide.

### S11 — PROVENANCE · verify, don't trust the machine [mermaid: one attestation root]
> Every actor that touches this — a commit, a workload, a human, a device — signs its work, to one cryptographic root. You can prove exactly which actor changed what, when, and from what evidence. For a business betting on AI doing real work, that's not a nice-to-have. That's the whole trust model.

### S12 — THE HONEST RED · twenty seven of twenty eight, live [real terminal: verify-all --live]
> Here's the whole thing, tested against itself, live, right now: twenty seven of twenty eight checks, green. And that one red check? I'm showing it to you on purpose. It's the fintech cluster's identity rollout, not finished yet. Nothing here gets rounded up to a hundred percent — and that's exactly the honesty this model demands of everyone else.

### S13 — WHAT GOT BUILT · the pace of execution [built stat block]
> And here's what it took to get here: six live organisations, a real signed estate, dozens of independent checks that all have to pass before anything ships — built and running, not roadmapped. This is what the team does with runway. This is the rate you're funding.

### S14 — WHY CONTROL PLANE, WHY NOW [mermaid: the hourglass, Flux at centre]
> Flux isn't a logo on a slide here — it's load-bearing. It's the plane distributing every signed policy, to every cluster, provably. Every board in the country is suddenly asking how they govern AI doing real work. Nobody else is answering with a live, priced, running system. We can own that answer first.

### S15 — THE VISION · risk on the balance sheet [mermaid: hourglass, balance-sheet line lit]
> Which is where this ends up: technological risk, as one line on the balance sheet. Priced the way an insurer prices it, moving the way a market moves it — a number your board can finally read, defend, and act on, instead of a wall of red, amber, green.

### S16 — THE ASK · give me the runway [clean close]
> So here's the ask. You've just watched it run — this isn't a pitch for an idea, it's a pitch for a system that already works. Fund the next stretch: finish the identity rollout on the two clusters still catching up, tour this in front of a real design partner, and turn twenty seven of twenty eight into a story every one of your customers wants to buy into. Back it, and technological risk goes on the balance sheet — proportionate, priced, and honest, live.

---

## Word count (spoken text only, per segment)

S1 46 · S2 42 · S3 51 · S4 33 · S5 62 · S6 47 · S7 55 · S8 51 · S9 46 · S10 66 · S11 55 · S12 71 ·
S13 47 · S14 60 · S15 51 · S16 87 — **total ≈ 870 words**

At the measured ~2.3–2.6 wps this drafts to roughly **335–380s** — under the 400s target, which is
the right side to draft on (easier to loosen pacing/add a beat than to cut a finished recording).
Real per-segment durations from actual TTS output decide the real adjustment, per the plan.
