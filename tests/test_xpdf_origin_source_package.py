"""Source preparation only: no build, converter invocation, PDF or native observation."""
import importlib.util
import os
from pathlib import Path
import sys

import pytest

SCRIPT = Path(__file__).parents[1] / 'bench/pinned-candidate/xpdf-origin/prepare_source.py'
spec = importlib.util.spec_from_file_location('xpdf_origin_prepare_source', SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_changed_archive_cannot_create_a_source_tree(tmp_path):
    archive = tmp_path / 'changed.tar.gz'
    archive.write_bytes(b'changed public archive')
    target = tmp_path / 'new-source'
    with pytest.raises(ValueError, match='archive'):
        module.prepare_source(archive, target)
    assert not target.exists()


def test_existing_source_directory_is_preserved(tmp_path):
    target = tmp_path / 'existing'
    target.mkdir()
    record = target / 'owned.txt'
    record.write_bytes(b'keep existing source')
    with pytest.raises(FileExistsError):
        module.prepare_source(tmp_path / 'not-needed.tar.gz', target)
    assert record.read_bytes() == b'keep existing source'
    assert sorted(p.name for p in target.iterdir()) == ['owned.txt']


def test_broken_destination_symlink_is_not_followed(tmp_path):
    target = tmp_path / 'link'
    target.symlink_to(tmp_path / 'absent')
    with pytest.raises(FileExistsError):
        module.prepare_source(tmp_path / 'not-needed.tar.gz', target)
    assert target.is_symlink() and not (tmp_path / 'absent').exists()


def test_pinned_archive_prepares_the_instrumented_build_source(tmp_path):
    supplied = os.environ.get('TWIN_XPDF_SOURCE_ARCHIVE')
    if not supplied:
        pytest.skip('explicit retained official archive not supplied; no download')
    prepared = module.prepare_source(Path(supplied), tmp_path / 'prepared')
    assert prepared.name == 'xpdf-4.06'
    assert (prepared / 'COPYING').read_bytes().startswith(b'\t\t    GNU GENERAL PUBLIC LICENSE')
    assert (prepared / 'xpdf/TwinOrigin.cc').is_file()
    assert (prepared / 'xpdf/TwinOrigin.h').is_file()
    assert not (prepared / 'xpdf/pdftotext').exists()
