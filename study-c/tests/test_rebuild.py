"""The rebuild must reproduce the published Study C numbers.

expected_published.json holds the numbers printed in the paper. They equal the output of the
original pre-registered analysis (run on 2026-10-04 on the full private data), which was checked
line by line against this rebuild on 2026-10-15, except H2's Holm-adjusted p, which carries the
correction described in the README (0.00015 instead of 0.00012). Run: python3 -m unittest discover -s tests
"""
import json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import rebuild  # noqa: E402

EXP = json.load(open(os.path.join(HERE, "expected_published.json")))
OUT = rebuild.rebuild(rebuild.load())


class Arms(unittest.TestCase):
    def test_arm_table(self):
        for arm, e in EXP["arms"].items():
            got = OUT["arms"][arm]
            self.assertEqual((got["units"], got["questions"]), (e["units"], e["questions"]), arm)
            for c in ("correct", "wrong", "unknown", "correct_blind"):
                self.assertEqual(round(got[c], 1), e[c], (arm, c))

    def test_family_table(self):
        for arm, fams in EXP["family_C2"].items():
            for f, v in fams.items():
                self.assertEqual(round(OUT["arms"][arm]["family_pooled"][f], 1), v, (arm, f))


class Holm(unittest.TestCase):
    """Regression for the analysis correction: Holm needs the running maximum."""

    def test_running_maximum(self):
        got = [round(x, 10) for x in rebuild.holm([0.01, 0.011, 0.20])]
        self.assertEqual(got, [0.03, 0.03, 0.2])

    def test_input_order_kept(self):
        got = [round(x, 10) for x in rebuild.holm([0.20, 0.011, 0.01])]
        self.assertEqual(got, [0.2, 0.03, 0.03])


class Tests(unittest.TestCase):
    def check(self, name):
        for x in OUT[name]:
            e = EXP[name][x["h"]]
            self.assertEqual(x["n"], e["n"])
            self.assertEqual(round(x["mean"], 1), e["mean"], (name, x["h"]))
            self.assertEqual([round(c, 1) for c in x["ci"]], e["ci"], (name, x["h"]))
            self.assertEqual(float("%.2g" % x["holm"]), e["holm"], (name, x["h"]))
            self.assertEqual([round(c, 1) for c in x["ci_agent"]], e["ci_agent"], (name, x["h"]))

    def test_primary(self):
        self.check("primary")

    def test_without_leaky_questions(self):
        self.check("noleak")

    def test_blind_check_rescore(self):
        self.check("blind")


if __name__ == "__main__":
    unittest.main()
