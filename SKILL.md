---
name: video-prompt-verifier
description: Reverse-engineer a reference video into an AI video prompt, then PROVE the prompt works — regenerate with it, score the render against the reference, fix the worst-scoring axis, and repeat until the score converges. Use when the user shares a reference video and wants a prompt that recreates it ("反推这个视频的提示词", "video to prompt", "make a prompt that reproduces this clip"), or wants to know how close a reversed prompt actually gets. Unlike plain video-to-prompt tools, the deliverable is the prompt PLUS its evidence: a score curve, per-round diffs, and side-by-side frames.
---

# video-prompt-verifier: a reverse prompt with a test report

A reversed prompt nobody tested is a guess. This skill treats the first reversed
prompt as a hypothesis and runs the loop that settles it:

```
probe → reverse (P0) → generate → score → fix ONE axis → regenerate → … → deliver prompt + evidence
```

## Hard rules (learned from the 2026-10-18 cat-deck test run)

1. **Fix the scoring method before the first generation.** Changing metrics
   mid-run invalidates the curve. Default stack:
   - Layer 1 (measured, optional): video-sharingan `analyze` + `compare`
     (camera speed, push-in rate, shot durations, audio class). Catches motion
     gaps that frame similarity misses. Needs opencv venv; its brief stage can
     crash on silent/sfx-only audio (analysis.json still survives — proceed).
   - Layer 2 (objective): `scripts/score_pair.py REF GEN` — per-frame hist
     correlation + global SSIM + pHash at 6 normalized timestamps, 0–100.
     Self-test first: ref vs ref must score 100.
   - Layer 3 (rubric): a viewer scores 5 axes × 20 — subject, action,
     environment, camera/framing, light & style — from contact sheets.
     Disclose who scored and that it is not blind.
2. **Measure the noise floor before claiming any improvement.** Generate P0
   at least twice with identical text. The spread between those scores is the
   noise band; a revision only counts if it beats the band.
3. **One axis per round.** Rewrite only the section of the prompt that owns
   the worst rubric axis (camera wording for camera, environment wording for
   environment…). Changing everything at once destroys attribution.
4. **Budget cap, stated up front.** Default: ≤3 revision rounds, low-res /
   draft generation where the engine offers it. Stop early when a round's
   gain falls inside the noise band.
5. **Validation runs need a best-of-N control.** When the point is to prove
   the loop (not just to serve one user clip), also draw P0 N times and keep
   its best score. The loop must beat same-prompt luck, and the report must
   state total generations spent by each side.
6. **Never claim "the original prompt".** The deliverable is a reconstructed
   prompt judged by how similar its output is — say so. (goodcase.ai's
   collection standard rejects source-less reversed prompts outright; the
   score evidence is what makes ours trustworthy.)

## Workflow

1. **Probe** the reference (ffprobe: duration, fps, size). Extract a contact
   sheet (6 frames across the duration) and actually look at it.
2. **Reverse → P0.** Structured fields: subject / action sequence /
   environment / camera & framing progression / light & style / duration &
   shot structure. Write P0 from the frames only, even if you know how the
   reference was made.
3. **Generate P0 twice** (same engine, same settings, same text). Score both.
   Record noise band and the worst rubric axis from the sheets.
4. **Revise one axis → P1.** Keep every other sentence byte-identical so the
   delta is attributable. Generate once, score, update the scorecard.
5. **Repeat** for the next-worst axis (P2, P3…) until the cap or convergence.
6. **(Validation mode)** Draw the extra P0 sample(s) for best-of-N.
7. **Deliver** (templates/scorecard.md format):
   - final prompt (copy-paste ready)
   - score table + curve chart (objective per round, noise band, best-of-N)
   - side-by-side contact-sheet montage (ref / P0 / … / final)
   - what each round changed and what it bought, in numbers
   - remaining gaps the loop did NOT close, named honestly
   - engine caveats (black-box prompt expansion, no seed control, n=…)

## Engine notes

- Any generator the user can run works (Muse media pipeline, Seedance /
  Kling / Veo APIs…). Keep the engine and settings fixed across all rounds
  of one test; note that some pipelines expand prompts internally, which adds
  variance the noise floor must absorb.
- Frame-similarity scores reward matched staging and timing. A semantically
  fine render with different timing will score low — that is what the rubric
  layer is for. Report layers separately; a combined score is a summary, not
  a replacement.

## Round-2 learnings (2026-10-18: action case, FPV case, long-video probe)

- **POV wording is a first-class axis for FPV / first-person references.**
  Generators may render the camera vehicle INTO the frame (a visible drone
  under the bridge). The fix that bought +21.6 objective points: state
  "first-person camera view only — the camera itself flies; no drone or
  aircraft is ever visible in the frame" and anchor the key camera event to
  a time fraction ("through the arch at the midpoint"). Check for
  vehicle-in-frame as a binary rubric item on any FPV reference.
- **The measured layer (video-sharingan) has a domain — and a
  reproducibility problem.** Its tracker was built for UI / launch films.
  On natural footage it is not even repeatable: the same dog-park file read
  64.6 px/s in one run and 497.7 px/s in the next, with entirely different
  move classifications, and a single-take FPV reference was fragmented
  into 5 "shots", most of them untracked. Cut detection itself is solid
  (frame-exact on a stitched clip), so use the measured layer for cuts /
  ASL / audio, and NEVER gate on its camera classification or speeds for
  natural footage — per-frame objective scores plus binary visual checks
  carry those cases. If a background analyze run gets restarted, distrust
  any numbers you did not read back from the final analysis.json on disk.
- **Long / multi-shot videos: segment first.** Verified: cut detection on a
  stitched 20.04 s two-shot clip found the splice at frame 240 / 10.021 s,
  frame-exact. Workflow = detect cuts → run this loop per shot → stitch →
  whole-film checks (per-shot scores, ASL, transitions). Cost scales
  linearly with shots × rounds; set a per-shot budget. Cross-shot identity
  consistency is the known unsolved risk — it has NOT been validated yet,
  and a single-take long shot beyond the generator's per-render cap cannot
  be regenerated whole at all; do not promise either.

## Files

- `scripts/score_pair.py` — layer-2 objective scorer (PIL + numpy only)
- `templates/scorecard.md` — run record / deliverable format
- Reference run: `test-runs/test1-cat-deck/REPORT.md`
  (cat-deck test: P0 objective 41.9 → P1 48.4 → P2 53.0, noise band 2.1,
  best-of-3 control 42.9)
