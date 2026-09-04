#!/usr/bin/env python3
"""Every green rests on an observation (ecosystem ticket 76).

Fourteen findings in REVIEW-2026-09-02 shared one root cause: a verify script printed `SKIP:`
and then exited 0, which talk/verify-all.sh grades PASS. Ticket 55 closed that class once and
seven scripts escaped it. This module is the class-level net: it reads every verify script the
gate discovers and names any `echo "SKIP ..."` statement that does not end in a could-not-look --
either because the script exits 0 straight after it, or because nothing exits at all and the
script carries on to its own PASS line (`verify-witness-set.sh`'s step 5, the escapee an exit-0
rule alone cannot see).

    every_green.py scan <dir>...     # one line per offender, exit 1 if any
    every_green.py selfcheck         # planted good and bad scripts grade as planted

Text, not execution: a script's absent-instrument branch cannot be exercised here without
removing the instrument, which each script's own --selfcheck does for itself. What this reads is
the shape that produced the false greens, so the shape cannot come back unnamed.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

SKIP_STATEMENT = re.compile(r"""^\s*(?:echo|printf)\s+['"]\s*SKIP\b""")
EXIT_ANY = re.compile(r"(?:^\s*|[;&|({]\s*)exit\s+(\d+)\b", re.M)
# How many executable statements after the SKIP echo an exit still belongs to it. The seven
# escapees were all one or two apart (a second echo line in between at most).
WINDOW = 3


def statements(text: str) -> list[tuple[int, str]]:
    """`(1-based line number, text)` per logical statement. A line whose double quotes are
    unbalanced runs on into the next, so a SKIP reason wrapped over two lines is one statement
    and the `exit 3` that closes it is not mistaken for a separate branch."""
    out: list[tuple[int, str]] = []
    buf, start = "", 0
    for n, line in enumerate(text.splitlines(), 1):
        if buf:
            buf += "\n" + line
        else:
            start, buf = n, line
        if buf.count('"') % 2 == 0:
            out.append((start, buf))
            buf = ""
    if buf:
        out.append((start, buf))
    return out


def offences(text: str) -> list[tuple[int, str]]:
    """`(line, shape)` for every SKIP statement that does not end in a could-not-look. Two
    shapes produced the fourteen findings:

    `exit 0`         the SKIP is printed and the script exits 0, which verify-all.sh grades
                     PASS -- six of the seven computed-semver escapees.
    `falls through`  the SKIP is printed and nothing exits at all; the script carries on to
                     its own PASS line -- verify-witness-set.sh's step 5, the one an exit-0
                     rule alone cannot see.

    An `exit 3` (or any non-zero exit) within WINDOW executable statements, including one on
    the SKIP's own statement, is the honest shape and is not named."""
    stmts = statements(text)
    found: list[tuple[int, str]] = []
    for i, (n, stmt) in enumerate(stmts):
        if not SKIP_STATEMENT.match(stmt):
            continue
        shape, seen = "falls through", 0
        for pos, follow in enumerate([stmt] + [s for _, s in stmts[i + 1:]]):
            if pos:
                stripped = follow.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                seen += 1
            hit = EXIT_ANY.search(follow)
            if hit:
                shape = "exit 0" if hit.group(1) == "0" else ""
                break
            if seen >= WINDOW:
                break
        if shape:
            found.append((n, shape))
    return found


def offenders(text: str) -> list[int]:
    """The 1-based line numbers `offences` names."""
    return [n for n, _ in offences(text)]


def scripts_under(*roots: str) -> list[str]:
    """The same discovery talk/verify-all.sh uses: verify*.sh, never under .work/ or .git/."""
    out: list[str] = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
            dirnames[:] = [d for d in dirnames if d not in (".git", ".work", "__pycache__")]
            out.extend(os.path.join(dirpath, f) for f in filenames
                       if f.startswith("verify") and f.endswith(".sh"))
    return sorted(out)


def scan(*roots: str) -> list[str]:
    """`path:line: shape` for every offence under the roots."""
    hits: list[str] = []
    for path in scripts_under(*roots):
        with open(path, encoding="utf-8", errors="replace") as fh:
            for n, shape in offences(fh.read()):
                hits.append(f"{path}:{n}: {shape}")
    return hits


def selfcheck() -> None:
    good = 'if ! command -v tool >/dev/null; then\n  echo "SKIP: tool absent"\n  exit 3\nfi\necho PASS\n'
    bad = 'if ! command -v tool >/dev/null; then\n  echo "SKIP: tool absent"\n  exit 0\nfi\necho PASS\n'
    two_line = 'echo "SKIP (step 5): tool absent"\necho "second line of the reason"\nexit 0\n'
    fell = 'if ! x; then\n  echo "SKIP (step 5): tool absent"\nelse\n  look\nfi\necho "PASS: all five steps"\n'
    same_line = 'x || { echo "SKIP: tool absent"; exit 3; }\necho PASS\n'
    commented = '# SKIPs (exit 0) if absent -- a comment, not a statement\necho "SKIP: x"\n# exit 0\nexit 3\n'
    wrapped = 'echo "SKIP: tool absent\n  (install it and re-run)"\nexit 3\n'
    assert offences(good) == [], offences(good)
    assert offences(bad) == [(2, "exit 0")], offences(bad)
    assert offences(two_line) == [(1, "exit 0")], offences(two_line)
    assert offences(fell) == [(2, "falls through")], offences(fell)
    assert offences(same_line) == [], offences(same_line)
    assert offences(commented) == [], offences(commented)
    assert offences(wrapped) == [], offences(wrapped)
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "u", ".work", "x"))
        with open(os.path.join(tmp, "u", "verify-bad.sh"), "w") as fh:
            fh.write(bad)
        with open(os.path.join(tmp, "u", "verify-good.sh"), "w") as fh:
            fh.write(good)
        with open(os.path.join(tmp, "u", ".work", "x", "verify-ignored.sh"), "w") as fh:
            fh.write(bad)
        with open(os.path.join(tmp, "u", "verify-fell.sh"), "w") as fh:
            fh.write(fell)
        hits = scan(tmp)
        assert hits == [os.path.join(tmp, "u", "verify-bad.sh") + ":2: exit 0",
                        os.path.join(tmp, "u", "verify-fell.sh") + ":2: falls through"], hits
    print("ok  selfcheck: a SKIP that exits 0, and a SKIP that exits nothing at all and lets the "
          "script reach its own PASS, are both named by line; an exit 3 (on its own line or the "
          "SKIP's), a comment, a wrapped reason and a .work/ copy are not")


def main(argv: list[str]) -> int:
    if not argv or argv[0] == "selfcheck":
        selfcheck()
        return 0
    if argv[0] != "scan" or len(argv) < 2:
        print(__doc__)
        return 2
    hits = scan(*argv[1:])
    for h in hits:
        print(f"  bad  {h}: a SKIP that verify-all.sh would grade PASS")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
