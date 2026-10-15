# Study C: blind recall test (pre-registration)

This is a lightly edited copy of the pre-registration. The original file (sha256 `1bcb180f…`) was committed before any answer was generated and has not changed since. Edits in this copy: agent, host and service names are removed and the owner's go-ahead is not quoted. The rules, numbers, arms, hypotheses and scorer are verbatim in meaning. The deviation note at the end was added for the paper.

Owner go-ahead 2026-10-04. Answerers: Claude Opus 5.5 subagents on a flat-rate subscription. Judge #1: an Opus 5.5 subagent. Judge #2: a second-vendor coding model in a clean, read-only directory. No metered API.

## Units and arms (built by the build script, seed 20261004)
- C1 rotation regime (`/clear` at 650K + brief): units = production rotations 20.09–04.10 whose new session read the full handoff brief (so arm C is exactly what an agent sees). 23 usable units, 192 questions (31 excluded: 23 without a read of the full brief, 8 with fewer than 5 questions).
  A = empty context | B = delivered head (the first injected brief block, at most about 9K characters) | C = the full brief file (as read by the new session).
- C2 native-compaction regime: units = the compactions of the earlier natural-experiment study. 31 usable, 225 questions (20 with fewer than 5 questions).
  A = empty | D = the client's native summary | E = the handoff brief at the SAME character budget as D | F = D + E.
- Questions: mechanical cloze from the agent's own pre-boundary text (probe families path/hash/fact/claim, at most 3 each, at most 12 per unit; the span is masked as ____). No LLM in question generation.
- Pilot: 4 units (2 C1 + 2 C2, random with the seed above) run first to test the pipeline; pilot units are EXCLUDED from analysis.

## Answering
One subagent per (unit, arm). It reads exactly one file holding the context of that arm only and the questions, and returns JSON [{qid, answer}]. Instruction: answer only from the context; if not there, answer "не знаю" ("I don't know"); no guessing. Audit: the subagent transcript must show no tool use except reading its own file; otherwise rerun once, then exclude (reported).

## Scoring
- Mechanical (primary): normalise (casefold, strip quotes, backticks and whitespace). Correct = the normalised answer contains the normalised key; for the fact family the key number must appear as a whole token. Unknown = empty or "не знаю"/unknown. Otherwise wrong.
- Judges (secondary): every non-unknown answer that is mechanically wrong goes to both judges blind (question, key, answer → equivalent yes/no). Judged-correct = mechanical OR both judges yes. Judge agreement (Cohen's kappa) reported. *(Not run; see the paper.)*
- Per-unit accuracy = correct / questions; hallucination rate = wrong (non-unknown) / questions.

## Hypotheses (one-sided, paired by unit; Holm correction over the 5 primary tests)
H1 C1: C > A.  H2 C1: C > B.  H3 C1: B > A.  H4 C2: E > D (brief vs native summary at equal budget).  H5 C2: F > D.
Secondary: hallucination rate per arm; per-family accuracy; judged vs mechanical agreement.
Stats: mean per-unit difference, paired bootstrap 95% CI (10,000, seed 20261004), cluster-by-agent CI, Wilcoxon signed-rank.
Nothing in this file changes after the first non-pilot answer.

## Addendum A1 (after pilot, before any main answer) 2026-10-04
The pilot (14 calls, excluded) showed the pipeline works: every subagent used exactly 1 tool call (a read of its own file), 5–9 s, 20–43K tokens; the empty arm answered "не знаю" 100%. Operational change only: in the main run each subagent writes its JSON answer file itself (allowed tools: read own call file + write own answer file = 2 tool calls), to remove transcription errors by the orchestrator. Audit: tool uses must be 2 and the answer file must exist; otherwise rerun once, then exclude.

## Addendum A2 (during the main run, BEFORE any main answer was scored) 2026-10-04
A subagent (empty arm) reported that some answers can be read off OTHER cloze lines of the same unit (cross-question leakage) and declined to use them. Leakage affects all arms of a unit identically but is not memory. Added a SENSITIVITY analysis (secondary, declared now, no main result seen): re-run H1–H5 excluding "leaky" questions, i.e. those whose normalised answer key appears verbatim in any other question's cloze text of the same unit. Primary analysis unchanged.

## Audit note (after the main run, before scoring) 2026-10-04
192/193 calls used exactly 2 tool calls. One C2 call (arm F) used 3 in the first run and again in the mandated single rerun: its 66K-character call file exceeds one read, so the subagent read the SAME own file twice (with an offset) and then wrote. Transcript checked, no other file touched. Accepted as compliant with the intent of A1 (read only its own file); the rerun answer is used.

*Correction (2026-10-15).* The count above is wrong for the pilot. Per A1, the 14 pilot calls made one tool call each (a read), and the orchestrator wrote their answer files; all 14 pilot answer files carry the same write time, 16:54:09Z. Accepted main-run calls: 179, of which 178 used exactly two tool calls and one used three; that one call was rerun once, the rerun also used three, and it was accepted. Subagents launched in total: 194 (14 pilot, 179 accepted main, 1 rerun).

## Deviation (added for the paper, 2026-10-15)
One change was not declared as an addendum. After the pilot and before any main-run answer, the build script was corrected so that arm B contains only the first injected brief block. The change was committed one minute after the pre-registration and before addendum A1. The protocol text above does not mention it.
