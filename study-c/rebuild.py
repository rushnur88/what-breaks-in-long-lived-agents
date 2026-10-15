#!/usr/bin/env python3
"""Rebuild the Study C tables, intervals and tests from data/study_c_units.csv.

Standard library only. The statistics follow the pre-registered analysis exactly:
per-unit accuracy, paired difference per unit, bootstrap over units (10,000 resamples,
random.Random(20261004), one generator shared by H1..H5 in that order), a normal-approximation
Wilcoxon signed-rank test with tie correction, one-sided p, and Holm over the five tests.

Usage:  python3 rebuild.py            # print everything
        python3 rebuild.py --json     # machine-readable output (used by tests/test_rebuild.py)
"""
import csv, json, math, os, random, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED, B = 20261004, 10000
FAM = ("path", "hash", "fact", "claim")
TESTS = (("H1", "C1", "C", "A"), ("H2", "C1", "C", "B"), ("H3", "C1", "B", "A"),
         ("H4", "C2", "E", "D"), ("H5", "C2", "F", "D"))


def load(path=os.path.join(HERE, "data", "study_c_units.csv")):
    rows = []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            for k, v in r.items():
                if k not in ("regime", "unit", "agent", "arm", "session_model"):
                    r[k] = int(v)
            rows.append(r)
    rows.sort(key=lambda r: r["order"])
    return rows


def boot(vals, rng):
    n = len(vals)
    ms = sorted(statistics.mean(rng.choice(vals) for _ in range(n)) for _ in range(B))
    return ms[int(0.025 * B)], ms[int(0.975 * B) - 1]


def cluster_boot(pairs, rng):
    by = {}
    for d, k in pairs:
        by.setdefault(k, []).append(d)
    keys = list(by)
    ms = sorted(statistics.mean([d for k in (rng.choice(keys) for _ in keys) for d in by[k]]) for _ in range(B))
    return ms[int(0.025 * B)], ms[int(0.975 * B) - 1], len(keys)


def wilcoxon(vals):
    v = [x for x in vals if abs(x) > 1e-12]
    n = len(v)
    if n == 0:
        return 0, 1.0
    order = sorted(range(n), key=lambda i: abs(v[i]))
    ranks, i, ties = [0.0] * n, 0, 0.0
    while i < n:
        j = i
        while j + 1 < n and abs(abs(v[order[j + 1]]) - abs(v[order[i]])) < 1e-12:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j + 2) / 2.0
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    wplus = sum(r for r, x in zip(ranks, v) if x > 0)
    mu = n * (n + 1) / 4.0
    sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0 - ties / 48.0)
    z = (wplus - mu) / sd if sd else 0.0
    return wplus, math.erfc(abs(z) / math.sqrt(2))


def unit_acc(rows, num="correct", den="n"):
    """(regime, unit, arm) -> percent, in file order; units with an empty denominator are dropped."""
    out = {}
    for r in rows:
        if r[den] > 0:
            out[(r["regime"], r["unit"], r["arm"])] = (100.0 * r[num] / r[den], r["agent"])
    return out


def tests(acc):
    rng = random.Random(SEED)
    res = []
    for label, regime, a, b in TESTS:
        by = {}
        for (rg, u, arm), (x, ag) in acc.items():
            if rg == regime:
                by.setdefault(u, {})[arm] = (x, ag)
        pairs = [(v[a][0] - v[b][0], v[a][1]) for v in by.values() if a in v and b in v]
        d = [x for x, _ in pairs]
        lo, hi = boot(d, rng)
        _, p = wilcoxon(d)
        m = statistics.mean(d)
        res.append({"h": label, "n": len(d), "mean": m, "ci": [lo, hi], "p": p / 2 if m > 0 else 1 - p / 2, "pairs": pairs})
    ranked = sorted(res, key=lambda x: x["p"])
    for i, x in enumerate(ranked):
        x["holm"] = min(1.0, x["p"] * (len(ranked) - i))
    crng = random.Random(SEED)
    for x in res:
        lo, hi, k = cluster_boot(x.pop("pairs"), crng)
        x["ci_agent"], x["n_agents"] = [lo, hi], k
    return res


def arm_table(rows):
    out = {}
    for r in rows:
        key = "%s/%s" % (r["regime"], r["arm"])
        out.setdefault(key, []).append(r)
    tab = {}
    for key, rs in out.items():
        tab[key] = {"units": len(rs), "questions": sum(r["n"] for r in rs)}
        for c in ("correct", "wrong", "unknown", "correct_blind"):
            tab[key][c] = statistics.mean(100.0 * r[c] / r["n"] for r in rs)
        tab[key]["family_pooled"] = {f: (100.0 * sum(r["correct_" + f] for r in rs) / sum(r["n_" + f] for r in rs))
                                     for f in FAM if sum(r["n_" + f] for r in rs)}
        tab[key]["context_chars_median"] = statistics.median(r["context_chars"] for r in rs)
    return tab


def rebuild(rows):
    return {"arms": arm_table(rows),
            "primary": tests(unit_acc(rows)),
            "noleak": tests(unit_acc(rows, "correct_noleak", "n_noleak")),
            "blind": tests(unit_acc(rows, "correct_blind"))}


def main():
    out = rebuild(load())
    if "--json" in sys.argv:
        json.dump(out, sys.stdout, indent=1)
        return
    print("Table: answers by arm (percent of questions, mean over units)")
    for k, v in sorted(out["arms"].items()):
        print("  %-5s units %2d  q %3d  correct %5.1f  wrong %4.1f  unknown %5.1f  blind %5.1f  chars(median) %7.0f"
              % (k, v["units"], v["questions"], v["correct"], v["wrong"], v["unknown"], v["correct_blind"], v["context_chars_median"]))
    for name in ("primary", "noleak", "blind"):
        print("Tests (%s):" % name)
        for x in out[name]:
            print("  %s n=%d  %+.1f [%+.1f, %+.1f]  one-sided p=%.3g  Holm=%.3g  agent-level CI [%+.1f, %+.1f] (%d agents)"
                  % (x["h"], x["n"], x["mean"], x["ci"][0], x["ci"][1], x["p"], x["holm"], x["ci_agent"][0], x["ci_agent"][1], x["n_agents"]))
    print("Appendix A: C2 accuracy by family (pooled over questions)")
    for arm in ("C2/D", "C2/E", "C2/F"):
        print("  %s %s" % (arm, ", ".join("%s %.1f" % (f, v) for f, v in out["arms"][arm]["family_pooled"].items())))


if __name__ == "__main__":
    main()
