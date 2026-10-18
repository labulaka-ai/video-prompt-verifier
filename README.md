# video-prompt-verifier

**A reversed video prompt is a guess until it has been regenerated and scored.**

中文简介：这个 skill 不止把参考视频「反推」成一段提示词——它会拿这段词真的去重新生成视频，与原片逐帧打分，找出差距最大的那一项，改词、重生成，直到分数收敛，最后交付「提示词＋测试报告」。没测过的反推词，在这里不算数。

Plain video-to-prompt tools hand you a paragraph and walk away. This skill treats the
first reversed prompt as a *hypothesis* and runs the loop that settles it:

```
probe → reverse (P0) → generate → score → fix ONE axis → regenerate → … → deliver prompt + evidence
```

The deliverable is never just the prompt. It is the prompt **plus its test report**:
the score curve, the noise floor it had to beat, a same-budget best-of-N control,
side-by-side frames, and the gaps the loop did *not* close — named honestly.

## Evidence (three test runs, 2026-10-18)

All runs used one fixed generation engine; objective score = per-frame histogram
correlation + global SSIM + pHash at 6 normalized timestamps (0–100, scorer in
[`scripts/score_pair.py`](scripts/score_pair.py), self-test ref-vs-ref = 100.0).

| Case | P0 | After targeted fixes | What moved it |
|---|---|---|---|
| Cat on a deck, 10 s single shot | 41.9 avg (3 draws, spread 2.1 = noise floor) | **53.0** (P2) | camera wording, then environment wording |
| Border collie catching a frisbee | 36.5 | **43.5** (P1) | environment: P0 invented a crowd of spectators; the reference park is empty |
| FPV drone through a stone arch | 51.5 | **73.1** (P1) | POV definition: P0 rendered a visible drone *into* the shot; "first-person view only, no aircraft in frame" fixed it (+21.6) |

Controls & honesty notes:

- In the cat run the loop beat the best of 3 identical-prompt draws (42.9) by **+10.1** —
  the gain is larger than same-prompt luck.
- In the round-2 runs P0 was drawn once per case (budget spent on breadth); the noise
  band from the cat run (2.1) was reused as the significance threshold. Both gains clear it.
- The rubric layer (5 axes × 20, scored from contact sheets, *not* blind) is reported
  separately in each run's report; the headline numbers above are the objective layer.
- One measurement tool we tried (video-sharingan's camera tracker) turned out to be
  **non-reproducible on natural footage** — the same file read 64.6 px/s in one run and
  497.7 px/s in the next. It is used in this repo only for cut detection, which *was*
  frame-exact: a stitched 20.04 s two-shot clip's splice was found at frame 240 / 10.021 s
  (see `test-runs/long-video-cuts/`).

## What's in this repo

```
SKILL.md                  the skill itself (rules, workflow, hard-won lessons)
scripts/score_pair.py     objective scorer (PIL + numpy + ffmpeg only)
templates/scorecard.md    the report format every run must deliver
test-runs/
  test1-cat-deck/         full first run: report, score chart, montage, all 6 videos
  test2-border-collie/    round-2 action case: videos + montage
  test3-fpv-bridge/       round-2 camera case: videos + montage
  long-video-cuts/        20 s two-shot splice + frame-exact cut detection output
  REPORT-round2.md        round-2 report (cases 2–3 + the long-video method)
```

## Use it

- **As an agent skill:** copy this folder into your agent's skills directory
  (e.g. `~/.claude/skills/video-prompt-verifier/` or your Muse custom-skills folder)
  and ask for a video to be reverse-engineered. The skill enforces the discipline:
  fix the scoring method first, measure the noise floor, change one axis per round,
  cap the budget, never claim the result is "the original prompt".
- **Just the scorer:** `python3 scripts/score_pair.py REF.mp4 GEN.mp4`
  (needs `ffmpeg`/`ffprobe`, Python PIL + numpy).

## Method rules (the short version)

1. Fix the scoring method *before* the first generation — changing metrics mid-run invalidates the curve.
2. Measure the noise floor (same prompt, ≥2 draws) before claiming any improvement.
3. One axis per round; keep every other sentence byte-identical so the delta is attributable.
4. Validation runs need a best-of-N control on the same budget.
5. Long videos are segmented at detected cuts and looped per shot — end-to-end multi-shot
   identity consistency is the known open risk and is *not* yet validated here.

## Limitations

- n = 3 reference clips, one generation engine (which expands prompts internally and
  offers no seed control — the noise floor absorbs some of that, not all).
- API engines with seed control (Seedance / Kling / Veo class) have not been tested yet.
- Frame-similarity rewards matched staging and timing; a semantically fine render with
  different timing scores low. That is what the rubric layer is for.

## License

Code and documentation: MIT (see `LICENSE`). Test videos were AI-generated for this
project and are shared under CC BY 4.0 — reuse with attribution.

Method and tests by **Labulaka**. The measured-layer experiments used
[video-sharingan](https://github.com/nikolasfaria/video-sharingan) (external tool, not vendored here).
