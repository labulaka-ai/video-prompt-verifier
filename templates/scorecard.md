# Run scorecard — <reference name>

- Reference: <file, duration, fps, size>
- Engine / settings (fixed all rounds): <…>
- Scoring fixed before generation: objective = score_pair.py (6 frames);
  rubric = subject/action/environment/camera/light ×20 by <who, blind or not>;
  measured layer (optional) = video-sharingan compare.

## Prompts
- P0 (reversed from frames only): <full text>
- P1 (axis changed: <axis>): <full text or exact diff>
- P2 (axis changed: <axis>): <…>

## Scores
| round | objective | rubric (S/A/E/C/L) | combined | notes |
|---|---|---|---|---|
| P0 #1 | | | | |
| P0 #2 | | | | noise band = |
| P0 best-of-N | | | | control |
| P1 | | | | |
| P2 | | | | |

## Verdict
- Beat the noise band? <yes/no, by how much>
- Beat best-of-N? <yes/no, by how much; generations spent each side>
- Remaining gaps (not closed): <…>
- Engine caveats: <…>
