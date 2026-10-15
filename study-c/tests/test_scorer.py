"""Behaviour of the frozen Study C scorer on synthetic answers.

These tests document what the scorer does, including its known failure modes, so a reader can
see exactly where a containment rule credits a wrong answer or misses a right one. They do not
claim the behaviour is desirable. Run: python3 -m unittest discover -s tests
"""
import os, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "scorer", "study_c_score.py")


def _load():
    src = open(SRC, encoding="utf-8").read()
    body = src.split("NOLEAK =")[0].replace("from bfleet_stats import boot, wilcoxon, SEED  # noqa: E402", "")
    ns = {"__file__": os.path.abspath(SRC)}
    exec(body, ns)
    return ns["verdict"]


verdict = _load()


def q(family, key):
    return {"family": family, "answer": key}


class Correct(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(verdict(q("path", "/srv/app/config.yaml"), "/srv/app/config.yaml"), "correct")

    def test_quotes_case_whitespace_ignored(self):
        self.assertEqual(verdict(q("hash", "a1b2c3d4"), "`A1B2 C3D4`"), "correct")

    def test_fact_whole_number(self):
        self.assertEqual(verdict(q("fact", "13"), "13 hours"), "correct")


class Unknown(unittest.TestCase):
    def test_forms(self):
        for a in ("", "unknown", "не знаю", "N/A", "-"):
            self.assertEqual(verdict(q("hash", "a1b2c3d4"), a), "idk", a)

    def test_unknown_wins_over_content(self):
        # an answer that says "I don't know" anywhere counts as unknown, even if it also guesses
        self.assertEqual(verdict(q("hash", "a1b2c3d4"), "не знаю, возможно a1b2c3d4"), "idk")


class KnownFalseCredit(unittest.TestCase):
    """Containment credits these although a human might not. None occurred among the 521 credited
    answers of the main run (paper, Study C, Scoring)."""

    def test_negation(self):
        self.assertEqual(verdict(q("claim", "preview"), "not preview"), "correct")

    def test_list_of_alternatives(self):
        self.assertEqual(verdict(q("path", "/srv/a.md"), "/srv/a.md or /srv/b.md"), "correct")

    def test_several_numbers(self):
        self.assertEqual(verdict(q("fact", "13"), "13 or 26"), "correct")


class KnownMiss(unittest.TestCase):
    """Correct in another form, scored wrong. The blind check found 16 such answers among 54."""

    def test_fact_not_whole_token(self):
        self.assertEqual(verdict(q("fact", "13"), "130"), "wrong")

    def test_path_without_leading_directories(self):
        self.assertEqual(verdict(q("path", "/home/user/shared/notes.md"), "shared/notes.md"), "wrong")

    def test_trailing_full_stop_in_key(self):
        self.assertEqual(verdict(q("claim", "preview."), "preview"), "wrong")

    def test_date_format(self):
        self.assertEqual(verdict(q("fact", "07.09"), "2026-09-07"), "wrong")


if __name__ == "__main__":
    unittest.main()
