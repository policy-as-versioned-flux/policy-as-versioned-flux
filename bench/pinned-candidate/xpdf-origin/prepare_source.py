#!/usr/bin/env python3
"""Prepare the exact reviewed source package; never fetch, build or run a converter."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile

ARCHIVE_SHA256 = '1c38f527c46caee0f712386d42a885b96a31ed9ce11904e872559859894d137e'
PACKAGE = Path(__file__).resolve().parent


def _bytes(path: Path, maximum: int) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('nonregular source package input')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(maximum + 1)
    finally:
        os.close(fd)
    if len(raw) > maximum:
        raise ValueError('source package input too large')
    return raw


def _matches(raw: bytes, pin: dict) -> bool:
    return len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256']


def archive_files(raw: bytes) -> dict[str, bytes]:
    """Return exact regular source bytes after complete fixed-archive preflight."""
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('official source archive hash differs')
    files: dict[str, bytes] = {}
    seen: set[str] = set()
    expanded = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as source:
        for index, member in enumerate(source):
            pieces = member.name.rstrip('/').split('/')
            name = '/'.join(pieces)
            if (index >= 4096 or not pieces or pieces[0] != 'xpdf-4.06'
                    or any(p in ('', '.', '..') for p in pieces) or '\\' in name or '\x00' in name
                    or name in seen or not (member.isdir() or member.isfile())
                    or member.issparse() or member.mode & 0o7000
                    or member.size < 0 or member.size > 4 * 1024 * 1024):
                raise ValueError('unsupported source archive member')
            seen.add(name)
            if member.isfile():
                if len(pieces) < 2:
                    raise ValueError('source archive root is a file')
                expanded += member.size
                if expanded > 32 * 1024 * 1024:
                    raise ValueError('source archive extent differs')
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError('source archive data absent')
                value = stream.read(member.size + 1)
                if len(value) != member.size:
                    raise ValueError('source archive truncated')
                files['/'.join(pieces[1:])] = value
    for name in files:
        if any(parent in files for parent in ['/'.join(name.split('/')[:i]) for i in range(1, len(name.split('/')))]):
            raise ValueError('source archive file/directory collision')
    if not files:
        raise ValueError('empty source archive')
    return files


def source_package() -> tuple[dict, dict[str, bytes]]:
    """Validate the one fixed package, independent of any patch execution."""
    pins = json.loads(_bytes(PACKAGE / 'SOURCE-PINS.json', 65536))
    if pins['schema'] != 'twin.xpdf-origin-source-package/v1' or pins['archive_sha256'] != ARCHIVE_SHA256:
        raise ValueError('source package identity differs')
    expected = {'xpdf-4.06-origin.patch', 'TwinOrigin.h', 'TwinOrigin.cc',
                'upstream-notices/README', 'upstream-notices/COPYING', 'upstream-notices/COPYING3'}
    if set(pins['package_files']) != expected:
        raise ValueError('source package members differ')
    package = {}
    for name in sorted(expected):
        value = _bytes(PACKAGE / name, 2 * 1024 * 1024)
        if not _matches(value, pins['package_files'][name]):
            raise ValueError('changed source package member: ' + name)
        package[name] = value
    return pins, package


def _directory_fd(path: Path) -> int:
    path = path.absolute()
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except OSError as error:
                raise ValueError('symlink or unsupported source parent') from error
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def materialize_source(files: dict[str, bytes], destination: Path) -> Path:
    """Write supplied preflighted bytes exclusively, descriptor-relative and no-follow."""
    if len(files) > 4096 or sum(map(len, files.values())) > 32 * 1024 * 1024:
        raise ValueError('source extent differs')
    for name, value in files.items():
        if (not name or '\\' in name or '\x00' in name or any(p in ('', '.', '..') for p in name.split('/'))
                or type(value) is not bytes or len(value) > 4 * 1024 * 1024):
            raise ValueError('unsupported source path/bytes')
    parent = _directory_fd(destination.parent)
    root = None
    try:
        os.mkdir(destination.name, 0o700, dir_fd=parent)
        root = os.open(destination.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        for name, value in sorted(files.items()):
            fd = os.dup(root)
            try:
                parts = name.split('/')
                for part in parts[:-1]:
                    try:
                        os.mkdir(part, 0o700, dir_fd=fd)
                    except FileExistsError:
                        pass
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                    os.close(fd)
                    fd = child
                out = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
                with os.fdopen(out, 'wb') as stream:
                    stream.write(value)
            finally:
                os.close(fd)
    finally:
        if root is not None:
            os.close(root)
        os.close(parent)
    for name, value in files.items():
        if _bytes(destination / name, 4 * 1024 * 1024) != value:
            raise ValueError('source materialization readback differs')
    return destination


def verify_prepared(prepared: Path, pins: dict) -> None:
    """Require the six exact accepted post-patch byte identities."""
    expected_sources = {'xpdf/CMakeLists.txt', 'xpdf/TextOutputDev.h', 'xpdf/TextOutputDev.cc',
                        'xpdf/pdftotext.cc', 'xpdf/TwinOrigin.h', 'xpdf/TwinOrigin.cc'}
    if set(pins['patched_sources']) != expected_sources:
        raise ValueError('patched source closure differs')
    for name in sorted(expected_sources):
        if not _matches(_bytes(prepared / name, 2 * 1024 * 1024), pins['patched_sources'][name]):
            raise ValueError('patched source bytes differ: ' + name)


def prepare_source(archive: Path, destination: Path) -> Path:
    """Keep the strict stock source-only operation; failures never delete predecessors."""
    if os.path.lexists(destination):
        raise FileExistsError(destination)
    files = archive_files(_bytes(archive, 8 * 1024 * 1024))
    pins, package = source_package()
    destination.mkdir(mode=0o700, parents=False)
    prepared = materialize_source(files, destination / 'xpdf-4.06')
    for name in ('TwinOrigin.h', 'TwinOrigin.cc'):
        with (prepared / 'xpdf' / name).open('xb') as output:
            output.write(package[name])
    # Source patching only. No configure/build/test/converter command is hidden here.
    patched = subprocess.run(['/usr/bin/patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i',
                              str(PACKAGE / 'xpdf-4.06-origin.patch')],
                             cwd=prepared, capture_output=True, timeout=30, check=False)
    (destination / 'PATCH-STDOUT.log').write_bytes(patched.stdout)
    (destination / 'PATCH-STDERR.log').write_bytes(patched.stderr)
    (destination / 'PATCH-RESULT.json').write_text(json.dumps({
        'schema': 'twin.xpdf-source-preparation/v1', 'archive_sha256': ARCHIVE_SHA256,
        'source_package_sha256': hashlib.sha256((PACKAGE / 'SOURCE-PINS.json').read_bytes()).hexdigest(),
        'patch_exit_code': patched.returncode, 'scope': 'source preparation only; no build or converter execution',
    }, indent=2, sort_keys=True) + '\n')
    if patched.returncode or re.search(rb'offset|fuzz|reject', patched.stdout + patched.stderr, re.I):
        raise ValueError('reviewed source patch failed')
    verify_prepared(prepared, pins)
    return prepared


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('retained_archive', type=Path)
    parser.add_argument('new_owned_destination', type=Path)
    args = parser.parse_args()
    print(prepare_source(args.retained_archive, args.new_owned_destination))


if __name__ == '__main__':
    main()
