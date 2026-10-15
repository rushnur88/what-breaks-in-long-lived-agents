# Study C: reproducibility package

Companion package for the preprint "What Breaks in Long-Lived Agents: An Eight-Month Operating Record of a Ten-Agent Fleet" (Ravshan Nuraliev, 2026), DOI 10.5281/zenodo.23404010.

This package lets a reader recompute every Study C number in the paper (Section 4, Study C; Appendix A) from per-unit counts. It needs only Python 3 and its standard library.

```
python3 rebuild.py                              # print both tables, all tests, Appendix A
python3 -m unittest discover -s tests -v        # scorer behaviour + rebuild == published numbers
```

## Contents

| path | what it is |
|---|---|
| `data/study_c_units.csv` | one row per (unit, arm) of the main run: 179 rows, 50 units, 8 agents |
| `rebuild.py` | rebuilds the arm table, the five hypothesis tests, bootstrap and agent-level intervals, Holm, both sensitivity analyses and the per-family table |
| `protocol/PROTOCOL_C_public.md` | the pre-registration with both addenda, the audit note and the deviation note; names removed |
| `scorer/study_c_score.py`, `scorer/SHA256` | the frozen mechanical scorer, byte-identical to the pre-registered one (sha256 `c4ae3421…`) |
| `tests/test_scorer.py` | the scorer on synthetic answers, including the cases where it credits a wrong answer or misses a right one |
| `tests/test_rebuild.py`, `tests/expected_published.json` | the rebuild must equal the numbers printed in the paper |

## Columns of `data/study_c_units.csv`

- `order`: position in the original call manifest. The pre-registered analysis iterates units in this order, and the bootstrap draws depend on it.
- `regime`: C1 (rotation) or C2 (native compaction). `unit`: pseudonymous event id. `agent`: pseudonymous agent id, for the agent-level intervals. `arm`: A–C (C1) or A, D–F (C2).
- `n`, `correct`, `wrong`, `unknown`: questions and mechanical verdicts. `n_<family>`, `correct_<family>`: the same by question family (path, hash, fact, claim).
- `n_noleak`, `correct_noleak`: the same after dropping questions whose key appears in another question of the unit (addendum A2).
- `correct_blind`: correct after the blind check, i.e. mechanical credit plus answers the check labelled "correct in another form".
- `context_chars`: length of the arm's context in characters.
- `session_model`: model family that ran the source session at the boundary (claude, glm or deepseek). In C2 the native summary was most likely written by this model; the transcripts do not name the summary's author.

## Analysis correction before publication

The pre-registered analysis script applied Holm's procedure without the running maximum. With it, H2's adjusted p is 0.00015 instead of 0.00012, in the primary analysis and in the blind-check rescoring; no decision changes. The frozen scorer is kept byte-identical; `rebuild.py` carries the correction.

The frozen scorer is an archival artifact (it imports an internal module that is not shipped); the public reproduction entry point is `rebuild.py`.

## What this package reproduces, and what it does not

It reproduces the computation: from these counts, `rebuild.py` gives every published table entry, interval and p-value exactly. On 2026-10-15 its output was compared line by line with the output of the original analysis, which ran on 2026-10-04 on the full data; the only difference is the Holm correction described above.

It does not reproduce the labels. The questions, answer keys and answers come from private production transcripts and are not released. Whether each key was extracted correctly from its transcript, and whether each verdict is right, can be checked only on the private data. Inside the fleet that check was done by a second node (independent re-implementation of the scorer, and the blind check of 114 answers described in the paper). From outside, it is a separate level of reproducibility that this package does not reach.

The blind-check labels were made by two agents independently, both blind to the arm and the second also blind to the first labels. They agreed on 113 of 114 items (Cohen's kappa 0.99 over four labels) and on all 114 as correct or not, so `correct_blind` is the same under either labelling.
