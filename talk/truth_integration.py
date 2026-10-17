"""Deterministic TRUTH integration over Git data, never a new measurement.

The caller verifies the original clock signature and current authority. This
module preserves the base tree outside TRUTH/captures, the original raw parent,
all prior log bytes, and every selected signed capture blob without checkout.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import tempfile


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def run(root: Path, *args: str, data: bytes | None = None, index: str | None = None) -> subprocess.CompletedProcess[bytes]:
    env = {key: value for key, value in os.environ.items()
           if key not in {'GH_TOKEN', 'GITHUB_TOKEN', 'TRUTH_READ_TOKEN',
                          'PAVC_OTHER_HAND_PRIVATE_KEY', 'GIT_INDEX_FILE', 'GIT_ASKPASS', 'SSH_ASKPASS'}
           and not key.startswith('GIT_CONFIG_')}
    if index is not None:
        env['GIT_INDEX_FILE'] = index
    try:
        return subprocess.run(['git', '-c', 'credential.helper=', '-c', 'core.hooksPath=' + os.devnull,
                               '-c', 'protocol.ext.allow=never', '-C', str(root), *args],
                              input=data, capture_output=True, timeout=60, env=env)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError('Git integration instrument is unavailable; delivery remains pending') from error


def git(root: Path, *args: str, data: bytes | None = None, index: str | None = None) -> bytes:
    result = run(root, *args, data=data, index=index)
    require(result.returncode == 0, 'Git cannot establish the TRUTH integration; delivery remains pending')
    return result.stdout


def mergeable(root: Path, base: str, original: str) -> bool:
    result = run(root, 'merge-tree', '--write-tree', base, original)
    require(result.returncode in (0, 1), 'Git cannot establish whether the original merges cleanly')
    return result.returncode == 0


def ancestor(root: Path, original: str, base: str) -> bool:
    result = run(root, 'merge-base', '--is-ancestor', original, base)
    require(result.returncode in (0, 1), 'Git cannot establish recorded original ancestry')
    return result.returncode == 0


def entries(root: Path, ref: str) -> dict[str, tuple[str, str, str]]:
    result = {}
    for row in git(root, 'ls-tree', '-rz', ref).split(b'\0'):
        if row:
            header, path = row.split(b'\t', 1)
            mode, kind, blob = header.decode().split()
            result[path.decode()] = (mode, kind, blob)
    return result


@dataclass(frozen=True)
class Integration:
    base: str
    original: str
    tree: str
    branch: str

    def validate(self, root: Path, head: str) -> None:
        parents = git(root, 'rev-list', '--parents', '-n', '1', head).decode().split()
        require(parents == [head, self.base, self.original], 'integration parents changed')
        require(git(root, 'rev-parse', head + '^{tree}').decode().strip() == self.tree,
                'integration tree does not preserve the signed observation and current declarations')
        raw = git(root, 'cat-file', 'commit', head)
        headers = raw.split(b'\n\n', 1)[0]
        require(b'\ngpgsig ' not in headers and b'\ngpgsig-sha256 ' not in headers,
                'integration must be explicitly unsigned, never a replacement clock signature')
        require(b'author observation delivery <observation-delivery@users.noreply.github.com>' in headers,
                'integration is not marked as non-measurement delivery')

    def commit(self, root: Path) -> str:
        # Explicit unsigned metadata never borrows the clock's author or signing key.
        head = git(root, '-c', 'user.name=observation delivery',
                   '-c', 'user.email=observation-delivery@users.noreply.github.com',
                   'commit-tree', self.tree, '-p', self.base, '-p', self.original, '--no-gpg-sign',
                   '-m', 'Integrate original TRUTH observation (not a measurement)\n\n'
                   + f'Original: {self.original}\nBase: {self.base}\n').decode().strip()
        self.validate(root, head)
        return head


def log(root: Path, base: str, original: str, suffix: str) -> bytes:
    """The same once-only log contract applies to clean and conflicting originals."""
    parents = git(root, 'rev-list', '--parents', '-n', '1', original).decode().split()
    require(len(parents) == 2, 'integration requires the original single-parent clock object')
    old = git(root, 'show', parents[1] + ':talk/truth.log')
    signed = git(root, 'show', original + ':talk/truth.log')
    line = suffix.encode()
    require(signed == old + line and line.startswith(b'TRUTH ') and line.endswith(b'\n')
            and len(line.splitlines()) == 1, 'integration suffix is not the exact signed single TRUTH row')
    current = git(root, 'show', base + ':talk/truth.log')
    require(current.startswith(old) and (not current or current.endswith(b'\n')),
            'current TRUTH rewrote the measured prefix')
    number = re.findall(rb'(?:^|\s)run=(\S+)', line)
    require(len(number) == 1 and not any(re.findall(rb'(?:^|\s)run=(\S+)', row) == number
                                       for row in current.splitlines()),
            'TRUTH run is already present or duplicated; integration remains pending')
    return current + line


def plan(root: Path, base: str, original: str, suffix: str, run_id: int, attempt: int) -> Integration:
    """Build only objects/index data; retain base-only captures and every outside entry."""
    require(all(re.fullmatch('[0-9a-f]{40}', ref) for ref in (base, original)), 'invalid integration object id')
    require(type(run_id) is int and run_id > 0 and type(attempt) is int and attempt > 0,
            'invalid integration run or attempt')
    new_log = log(root, base, original, suffix)
    parents = git(root, 'rev-list', '--parents', '-n', '1', original).decode().split()
    changed = git(root, 'diff-tree', '--no-commit-id', '--name-status', '--no-renames', '-r', '-z',
                  parents[1], original).split(b'\0')[:-1]
    require(bool(changed) and len(changed) % 2 == 0, 'original changed-path instrument is invalid')
    for status, path in zip(changed[::2], changed[1::2]):
        require(status in (b'A', b'M') and (path == b'talk/truth.log' or path.startswith(b'talk/captures/')),
                'TRUTH integration supports only the original log and capture changes')
    before, observed = entries(root, base), entries(root, original)
    captures = {p: v for p, v in observed.items() if p.startswith('talk/captures/')}
    require(all(mode == '100644' and kind == 'blob' for mode, kind, _ in captures.values()),
            'signed capture tree contains an unsafe object')
    require(observed.get('talk/truth.log', ())[:2] == ('100644', 'blob')
            and before.get('talk/truth.log', ())[:2] == ('100644', 'blob'), 'TRUTH log is not a regular blob')
    blob = git(root, 'hash-object', '-w', '--stdin', data=new_log).decode().strip()
    updates = {**captures, 'talk/truth.log': ('100644', 'blob', blob)}
    with tempfile.TemporaryDirectory(prefix='truth-integration-') as directory:
        index = str(Path(directory) / 'index')
        git(root, 'read-tree', base, index=index)
        data = b''.join(f'{mode} {kind} {sha}\t{path}'.encode() + b'\0'
                        for path, (mode, kind, sha) in updates.items())
        git(root, 'update-index', '-z', '--index-info', data=data, index=index)
        tree = git(root, 'write-tree', index=index).decode().strip()
    expected = {**before, **updates}
    require(entries(root, tree) == expected, 'integration changed an unselected base entry')
    return Integration(base, original, tree, f'integrations/truth/{run_id}-{attempt}/{base}')
