#!/usr/bin/env python3
"""Prepare the exact reviewed source package; never fetch, build or run a converter."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

ARCHIVE_SHA256 = '1c38f527c46caee0f712386d42a885b96a31ed9ce11904e872559859894d137e'
PACKAGE = Path(__file__).resolve().parent


def _bytes(path: Path, maximum: int) -> bytes:
    if path.is_symlink():
        raise ValueError('symlink source package input')
    with path.open('rb') as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError('source package input too large')
    return raw


def _matches(raw: bytes, pin: dict) -> bool:
    return len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256']


def prepare_source(archive: Path, destination: Path) -> Path:
    """Verify fixed source bytes and apply the reviewed patch in a new owned directory.

    Existing destinations, including broken links, are never reused. On a failed
    patch the new owned source is left for inspection; no predecessor is deleted.
    """
    if os.path.lexists(destination):
        raise FileExistsError(destination)
    raw = _bytes(archive, 8 * 1024 * 1024)
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('official source archive hash differs')
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
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as source:
        members = source.getmembers()
        if len(members) > 4096 or sum(m.size for m in members) > 32 * 1024 * 1024:
            raise ValueError('source archive extent differs')
        for member in members:
            path = Path(member.name)
            if (not path.parts or path.parts[0] != 'xpdf-4.06' or path.is_absolute()
                    or '..' in path.parts or not (member.isdir() or member.isfile())
                    or member.size > 4 * 1024 * 1024):
                raise ValueError('unsupported source archive member')
        destination.mkdir(mode=0o700, parents=False)
        source.extractall(destination, members=members, filter='data')
    prepared = destination / 'xpdf-4.06'
    for name in ('TwinOrigin.h', 'TwinOrigin.cc'):
        with (prepared / 'xpdf' / name).open('xb') as output:
            output.write(package[name])
    # Source patching only. No configure/build/test/converter command is hidden here.
    patched = subprocess.run(['/usr/bin/patch', '--batch', '--forward', '-p1', '-i',
                              str(PACKAGE / 'xpdf-4.06-origin.patch')],
                             cwd=prepared, capture_output=True, timeout=30, check=False)
    (destination / 'PATCH-STDOUT.log').write_bytes(patched.stdout)
    (destination / 'PATCH-STDERR.log').write_bytes(patched.stderr)
    (destination / 'PATCH-RESULT.json').write_text(json.dumps({
        'schema': 'twin.xpdf-source-preparation/v1', 'archive_sha256': ARCHIVE_SHA256,
        'source_package_sha256': hashlib.sha256((PACKAGE / 'SOURCE-PINS.json').read_bytes()).hexdigest(),
        'patch_exit_code': patched.returncode, 'scope': 'source preparation only; no build or converter execution',
    }, indent=2, sort_keys=True) + '\n')
    if patched.returncode:
        raise ValueError('reviewed source patch failed')
    expected_sources = {'xpdf/CMakeLists.txt', 'xpdf/TextOutputDev.h', 'xpdf/TextOutputDev.cc',
                        'xpdf/pdftotext.cc', 'xpdf/TwinOrigin.h', 'xpdf/TwinOrigin.cc'}
    if set(pins['patched_sources']) != expected_sources:
        raise ValueError('patched source closure differs')
    for name in sorted(expected_sources):
        if not _matches(_bytes(prepared / name, 2 * 1024 * 1024), pins['patched_sources'][name]):
            raise ValueError('patched source bytes differ: ' + name)
    return prepared


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('retained_archive', type=Path)
    parser.add_argument('new_owned_destination', type=Path)
    args = parser.parse_args()
    print(prepare_source(args.retained_archive, args.new_owned_destination))


if __name__ == '__main__':
    main()
