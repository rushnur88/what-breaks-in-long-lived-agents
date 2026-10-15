# What Breaks in Long-Lived Agents

Companion repository for the preprint

> Ravshan Nuraliev. *What Breaks in Long-Lived Agents: An Eight-Month Operating Record of a Ten-Agent Fleet.* Preprint, not peer-reviewed, October 2026. https://doi.org/10.5281/zenodo.23404010

## Abstract

Most agent benchmarks score a task in a fresh context, and newer memory benchmarks probe recall across sessions. Some costly failures can occur in one session but become visible and accumulate only over months. We report eight months of operating a fleet that grew to ten long-lived coding agents (nine on Claude Code) on four machines. First, *false zeros*: empty tool results taken as proof of absence. We list eighteen carriers and quantified cases such as 64 of 1,501 memory files silently dropped at a permission boundary. Second, verification needs a different position or instrument: a guard change that passed its author's check let through 52 commands its predecessor blocked. Third, we measure where a 1M-token window goes. The model's own output is the largest share (39%), and tool-server responses are below 1%. After a client update, idle compaction began to fire, visible only in its timing. A pre-registered blind study shows a full handoff brief restores 70.7% of probed facts after rotation, against 0% without it, but loses to the native summary under the same character limit. Fourth, we report negative results, including a mood classifier that did not beat "always neutral".

## What is here

| path | what it is |
|---|---|
| `paper/` | the preprint as PDF |
| `study-c/` | the reproducibility package for Study C (Section 4 and Appendix A): per-unit counts under pseudonymous ids, the pre-registration, the frozen scorer, a rebuild script and tests. See `study-c/README.md` |

To recompute the Study C tables, intervals and tests (Python 3, standard library only):

```
cd study-c
python3 rebuild.py
python3 -m unittest discover -s tests -v
```

The package reproduces the computation from per-unit counts. The questions, answer keys and answers come from private production transcripts and are not released, so the labels themselves cannot be re-checked from outside. `study-c/README.md` explains what this does and does not cover.

## Citation

```bibtex
@misc{nuraliev2026whatbreaks,
  author       = {Nuraliev, Ravshan},
  title        = {What Breaks in Long-Lived Agents: An Eight-Month Operating Record of a Ten-Agent Fleet},
  year         = {2026},
  month        = oct,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.23404010},
  url          = {https://doi.org/10.5281/zenodo.23404010},
  note         = {Preprint, not peer-reviewed}
}
```

## License

Code (`*.py`): MIT, see `LICENSE`. The paper, data tables and documentation: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
