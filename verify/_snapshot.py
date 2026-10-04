"""Committed local adopter copies for probes that need immutable Git objects."""
from pathlib import Path
import subprocess


def committed_repository(repo: Path, dest: Path) -> None:
    """Clone HEAD and its tag/history context without copying working-tree edits.

    The source is a local checkout. Preserve its observed origin/main ref rather
    than letting clone label the source's current probe branch as origin/main.
    All mutations occur in the disposable destination.
    """
    repo = repo.resolve()

    def source(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       text=True).strip()

    if source("rev-parse", "--show-toplevel") != str(repo):
        raise ValueError("probe source must be its own Git repository")
    commit = source("rev-parse", "HEAD")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", "--no-checkout",
                    str(repo), str(dest)], check=True)
    refs = source("for-each-ref", "--format=%(refname) %(objectname) %(symref)",
                  "refs/remotes/origin/")
    rows = [row.split() for row in refs.splitlines()]
    for sha in {commit, *(row[1] for row in rows)}:
        present = subprocess.run(["git", "-C", str(dest), "cat-file", "-e", sha],
                                 capture_output=True)
        if present.returncode:
            # The immutable source object is fetched locally, never from the forge.
            subprocess.run(["git", "-C", str(dest), "fetch", "--quiet", "--no-tags",
                            str(repo), sha], check=True)
        subprocess.run(["git", "-C", str(dest), "cat-file", "-e", sha], check=True)
    # A clone invents origin/<source local branch>. Only the source checkout's
    # actual observed remote refs may answer dated-history questions in a probe.
    existing = subprocess.check_output([
        "git", "-C", str(dest), "for-each-ref", "--format=%(refname)",
        "refs/remotes/origin/"], text=True).splitlines()
    for ref in existing:
        subprocess.run(["git", "-C", str(dest), "update-ref", "--no-deref", "-d", ref], check=True)
    for row in rows:
        ref, sha = row[:2]
        if len(row) == 3:
            subprocess.run(["git", "-C", str(dest), "symbolic-ref", ref, row[2]], check=True)
        else:
            subprocess.run(["git", "-C", str(dest), "update-ref", "--no-deref", ref, sha], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "--quiet", "--detach", commit],
                   check=True)
