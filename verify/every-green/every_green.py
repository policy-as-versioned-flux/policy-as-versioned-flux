#!/usr/bin/env python3
"""Every green rests on an observation (ecosystem ticket 76).

Fourteen findings in REVIEW-2026-09-02 shared one root cause: a verify script printed `SKIP:`
and then exited 0, which talk/verify-all.sh grades PASS. Ticket 55 closed that class once and
seven scripts escaped it. This module is the class-level net: it reads every verify script the
gate discovers and names any statement that PRINTS THE SKIP VERDICT TOKEN and does not end in a
could-not-look -- either because the script exits 0 straight after it, or because nothing exits
at all and the script carries on to its own PASS line (`verify-witness-set.sh`'s step 5, the
escapee an exit-0 rule alone cannot see).

    every_green.py scan <dir>...     # one line per offender; exit 1 if any, 3 if none but a
                                     # discovered script could not be read at all (a
                                     # could-not-read is a could-not-look), 0 otherwise
    every_green.py selfcheck         # planted good and bad scripts grade as planted

WHAT IS GRADED, AND WHAT IS NOT (the honest boundary; ticket 76 review, 2026-09-04). Graded: a
print statement -- `echo`, `printf`, or the estate's `say`/`note`/`warn`/`log` wrappers, with or
without flags, quotes or a colour escape -- whose FIRST PRINTED TOKEN is `SKIP`. That token is
the estate's verdict word: talk/verify-all.sh reads the last line of a script, so a statement
that spends `SKIP` is announcing the run's own outcome, and reaching exit 0 after it is a
contradiction no reading of the script can excuse.

NOT graded: a could-not-look announced in prose -- `echo "(skipped: kyverno CLI not found)"`,
`say "4. skipped: kubectl absent"`, `echo "  offline: ..."` -- because whether the PASS that
follows is a false green depends on what the PASS SENTENCE claims, which no regex reads. Both
kinds live in this estate. verify-proportionality.sh:75 and verify-provenance.sh:48 printed a
prose skip and then asserted the whole claim including the half they had not looked at: false
greens, fixed by this ticket. tuppence/reset/verify-reach-secrets.sh and platform/oscal/
verify-upflow.sh print one too and then narrow the closing sentence to what they did observe:
not false greens. A vocabulary net (skip-word + absence-word) was measured against all 95
discovered scripts on 2026-09-04 and named all four the same, so it would have to be believed
about the two it is wrong about. What catches the prose kind is not text but execution: the
per-script `selfcheck_absent` leg (verify/lib-observation.sh, .estate-clone/platform/lib.sh),
which re-runs the script with the instrument hidden and requires exit 3 with a `SKIP:` last line.
That is a per-script obligation and this net cannot impose it. The shell counts, on each run, how many
discovered scripts carry the leg; a prose could-not-look in any of the rest is graded by nothing,
and giving those scripts the leg is its own ticket.

Text, not execution: a script's absent-instrument branch cannot be exercised here without
removing the instrument, which each script's own --selfcheck does for itself. What this reads is
the shape that produced the false greens, so the shape cannot come back unnamed.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile

# A statement whose first printed token is the SKIP verdict word, in any print form the estate
# uses: `echo`/`printf`, the `say`/`note`/`warn`/`log` wrappers, `echo -e`, a leading colour
# escape or the `==>` prefix, quoted or bare. Widened on 2026-09-04 from `echo|printf` + quote:
# over the 95 scripts the gate discovers both spellings match the same 26 statements, so the
# widening costs nothing today and catches `say "SKIP: ..."` tomorrow.
SKIP_STATEMENT = re.compile(r"""
    ^\s*
    (?:echo|printf|say|note|warn|log)
    (?:\s+-{1,2}[A-Za-z]*)*
    \s+
    (?:['"]\s*)?
    (?:\\033\[[0-9;]*m|\\e\[[0-9;]*m|==>|\s)*
    SKIP\b
""", re.X)
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


def scripts_under(*roots: str, errors: list[str] | None = None) -> list[str]:
    """The same discovery talk/verify-all.sh uses: verify*.sh, never under .work/ or .git/.

    A root that is not a directory (a dangling symlink, a path that never existed) and a
    directory os.walk cannot read are appended to `errors` when one is given, rather than
    walked as empty: a tree that could not be read has not been observed to be clean."""
    out: list[str] = []
    for root in roots:
        if errors is not None and not os.path.isdir(root):
            errors.append(f"{root}: not a readable directory")
            continue
        for dirpath, dirnames, filenames in os.walk(
                root, followlinks=True,
                onerror=(None if errors is None
                         else lambda e: errors.append(f"{e.filename}: {e.strerror or e}"))):
            dirnames[:] = [d for d in dirnames if d not in (".git", ".work", "__pycache__")]
            out.extend(os.path.join(dirpath, f) for f in filenames
                       if f.startswith("verify") and f.endswith(".sh"))
    return sorted(out)


def read_tree(*roots: str) -> tuple[list[str], list[str]]:
    """`(offences, could-not-read)`. The first is `path:line: shape` per offence; the second is
    `path: reason` for every discovered script that could not be opened -- a dangling symlink
    (verify/demo/verify-demo.sh is one when talk/ is not checked out beside it), a permission,
    a vanished file. A could-not-read is a could-not-look: the scan did not observe that script
    to be clean, so it is reported as unlooked and never counted as clean."""
    hits: list[str] = []
    unread: list[str] = []
    for path in scripts_under(*roots, errors=unread):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            unread.append(f"{path}: {exc.strerror or exc}")
            continue
        for n, shape in offences(text):
            hits.append(f"{path}:{n}: {shape}")
    return hits, sorted(unread)


def scan(*roots: str) -> list[str]:
    """`path:line: shape` for every offence under the roots."""
    return read_tree(*roots)[0]


def selfcheck() -> None:
    good = 'if ! command -v tool >/dev/null; then\n  echo "SKIP: tool absent"\n  exit 3\nfi\necho PASS\n'
    bad = 'if ! command -v tool >/dev/null; then\n  echo "SKIP: tool absent"\n  exit 0\nfi\necho PASS\n'
    two_line = 'echo "SKIP (step 5): tool absent"\necho "second line of the reason"\nexit 0\n'
    fell = 'if ! x; then\n  echo "SKIP (step 5): tool absent"\nelse\n  look\nfi\necho "PASS: all five steps"\n'
    same_line = 'x || { echo "SKIP: tool absent"; exit 3; }\necho PASS\n'
    commented = '# SKIPs (exit 0) if absent -- a comment, not a statement\necho "SKIP: x"\n# exit 0\nexit 3\n'
    wrapped = 'echo "SKIP: tool absent\n  (install it and re-run)"\nexit 3\n'
    wrapper = 'say "SKIP: tool absent"\nexit 0\n'
    coloured = 'printf -- \'\\033[1;36mSKIP: %s\\n\' "tool absent"\nexit 0\n'
    prose = 'echo "  (skipped: tool not found -- the live half is unavailable here)"\necho "PASS: x"\n'
    assert offences(good) == [], offences(good)
    assert offences(bad) == [(2, "exit 0")], offences(bad)
    assert offences(two_line) == [(1, "exit 0")], offences(two_line)
    assert offences(fell) == [(2, "falls through")], offences(fell)
    assert offences(same_line) == [], offences(same_line)
    assert offences(commented) == [], offences(commented)
    assert offences(wrapped) == [], offences(wrapped)
    assert offences(wrapper) == [(1, "exit 0")], offences(wrapper)
    assert offences(coloured) == [(1, "exit 0")], offences(coloured)
    # The boundary this net does not cross: a could-not-look worded as prose is not the verdict
    # token and is not named, because whether the PASS after it overclaims is a question about
    # the sentence, not the shape. The script's own selfcheck_absent leg is what grades those.
    assert offences(prose) == [], offences(prose)
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
        hits, unread = read_tree(tmp)
        assert hits == [os.path.join(tmp, "u", "verify-bad.sh") + ":2: exit 0",
                        os.path.join(tmp, "u", "verify-fell.sh") + ":2: falls through"], hits
        assert unread == [], unread
        # A dangling symlink is a discovered script that cannot be read. It used to raise
        # FileNotFoundError out of scan() and the shell printed a FAIL that named nothing.
        os.symlink(os.path.join(tmp, "u", "gone.sh"), os.path.join(tmp, "u", "verify-dangling.sh"))
        hits, unread = read_tree(tmp, os.path.join(tmp, "no-such-root"))
        assert len(hits) == 2, hits
        assert [u.split(": ")[-1] for u in unread] == ["not a readable directory",
                                                       "No such file or directory"], unread
    print("ok  selfcheck: a SKIP that exits 0, and a SKIP that exits nothing at all and lets the "
          "script reach its own PASS, are both named by line, in every print form; an exit 3 (on "
          "its own line or the SKIP's), a comment, a wrapped reason, a prose skip and a .work/ "
          "copy are not; a script that cannot be read is reported as unlooked, not as clean")


def main(argv: list[str]) -> int:
    if not argv or argv[0] == "selfcheck":
        selfcheck()
        return 0
    if argv[0] != "scan" or len(argv) < 2:
        print(__doc__)
        return 2
    hits, unread = read_tree(*argv[1:])
    for h in hits:
        print(f"  bad  {h}: a SKIP that verify-all.sh would grade PASS")
    for u in unread:
        print(f"  ??   could not read {u}: this script was not observed to be clean")
    if hits:
        return 1
    return 3 if unread else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
