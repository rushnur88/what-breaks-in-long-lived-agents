#!/usr/bin/env python3
"""Study C — mechanical scoring + primary stats (PROTOCOL_C.md). Reads items/answers/<cid>.json."""
import glob, json, os, random, re, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from bfleet_stats import boot, wilcoxon, SEED  # noqa: E402

IDK = re.compile(r"^\s*(не\s*знаю|unknown|n/?a|нет данных|-+)?\s*\.?\s*$", re.I)


def norm(s):
    return re.sub(r"[\s`'\"«»“”*]+", "", (s or "").casefold())


def verdict(q, ans):
    a = (ans or "").strip()
    if IDK.match(a) or "не знаю" in a.casefold():
        return "idk"
    if q["family"] == "fact":
        ok = q["answer"] in re.findall(r"\d[\d.,:%]*\d|\d", a)
    else:
        ok = norm(q["answer"]) in norm(a)
    return "correct" if ok else "wrong"


def leaky(u):
    """A2: questions whose normalized key appears verbatim in another question's cloze of the same unit."""
    out = set()
    for q in u["questions"]:
        k = norm(q["answer"])
        if len(k) >= 2 and any(k in norm(o["cloze"]) for o in u["questions"] if o is not q):
            out.add(q["qid"])
    return out


NOLEAK = "--noleak" in sys.argv


def load():
    units = {u["unit"]: u for u in json.load(open(os.path.join(ROOT, "items", "units.json")))}
    if NOLEAK:
        for u in units.values():
            if "questions" in u:
                lk = leaky(u)
                u["questions"] = [q for q in u["questions"] if q["qid"] not in lk] or u["questions"][:0]
    man = json.load(open(os.path.join(ROOT, "items", "manifest.json")))
    rows = []
    for m in man:
        p = os.path.join(ROOT, "items", "answers", m["cid"] + ".json")
        if not os.path.exists(p):
            continue
        ans = {a["qid"]: a.get("answer", "") for a in json.load(open(p))}
        u = units[m["unit"]]
        vs = [verdict(q, ans.get(q["qid"])) for q in u["questions"]]
        n = len(vs)
        if n == 0:
            continue
        rows.append({**m, "bot": u["bot"], "n": n, "acc": 100 * vs.count("correct") / n,
                     "hall": 100 * vs.count("wrong") / n, "idk": 100 * vs.count("idk") / n,
                     "by_family": {f: [v for q, v in zip(u["questions"], vs) if q["family"] == f]
                                   for f in ("path", "hash", "fact", "claim")}})
    return rows


def compare(rows, study, a, b, label, rng):
    by = {}
    for r in rows:
        if r["study"] == study and not r["pilot"]:
            by.setdefault(r["unit"], {})[r["arm"]] = r
    pairs = [(u["%s" % a]["acc"] - u["%s" % b]["acc"], u[a]["bot"]) for u in by.values() if a in u and b in u]
    if len(pairs) < 3:
        print("  %s: n=%d (not enough)" % (label, len(pairs)))
        return None
    d = [x for x, _ in pairs]
    lo, hi = boot(d, rng)
    _, p = wilcoxon(d)
    p1 = p / 2 if statistics.mean(d) > 0 else 1 - p / 2
    print("  %s: n=%d | mean diff %+.1f pts, 95%% CI [%+.1f, %+.1f], one-sided Wilcoxon p=%.3g"
          % (label, len(d), statistics.mean(d), lo, hi, p1))
    return {"label": label, "n": len(d), "mean": statistics.mean(d), "ci": [lo, hi], "p": p1}


def main():
    rows = load()
    pilot = "--pilot" in sys.argv
    sel = [r for r in rows if r["pilot"] == pilot]
    print("answered calls: %d (%s)" % (len(sel), "pilot" if pilot else "main"))
    for st in ("C1", "C2"):
        for arm in sorted({r["arm"] for r in sel if r["study"] == st}):
            s = [r for r in sel if r["study"] == st and r["arm"] == arm]
            print("  %s arm %s: units %d | accuracy %.1f%% | hallucination %.1f%% | idk %.1f%%"
                  % (st, arm, len(s), statistics.mean(r["acc"] for r in s), statistics.mean(r["hall"] for r in s),
                     statistics.mean(r["idk"] for r in s)))
    if pilot:
        return
    rng = random.Random(SEED)
    tests = [compare(rows, "C1", "C", "A", "H1 C1 C>A", rng), compare(rows, "C1", "C", "B", "H2 C1 C>B", rng),
             compare(rows, "C1", "B", "A", "H3 C1 B>A", rng), compare(rows, "C2", "E", "D", "H4 C2 E>D", rng),
             compare(rows, "C2", "F", "D", "H5 C2 F>D", rng)]
    t = sorted([x for x in tests if x], key=lambda x: x["p"])
    m = len(t)
    print("Holm:", ", ".join("%s p=%.3g adj<=%.3g %s" % (x["label"], x["p"], min(1, x["p"] * (m - i)),
                                                        "SIG" if x["p"] * (m - i) < 0.05 else "ns")
                             for i, x in enumerate(t)))
    json.dump({"tests": tests, "rows": rows}, open(os.path.join(ROOT, "results", "study_c%s.json" % ("_noleak" if NOLEAK else "")), "w"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
