"""Source preparation only: no build, converter invocation, PDF or native observation."""
import importlib.util
import os
from pathlib import Path
import sys
import hashlib
import io
import tarfile

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


def test_shared_archive_validation_rejects_duplicate_alias_before_writes(tmp_path, monkeypatch):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w:gz') as archive:
        for name in ('xpdf-4.06/A', 'xpdf-4.06/./A'):
            info = tarfile.TarInfo(name)
            info.size = 1
            archive.addfile(info, io.BytesIO(b'A'))
    content = raw.getvalue()
    monkeypatch.setattr(module, 'ARCHIVE_SHA256', hashlib.sha256(content).hexdigest())
    with pytest.raises(ValueError, match='archive'):
        module.archive_files(content)
    assert list(tmp_path.iterdir()) == []


def test_shared_materialization_cannot_follow_an_existing_parent_link(tmp_path):
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    parent = tmp_path / 'parent'
    parent.symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        module.materialize_source({'A': b'TEST_ONLY'}, parent / 'new')
    assert not (elsewhere / 'new').exists()


@pytest.mark.parametrize('name,kind,mode,size', [
    ('/xpdf-4.06/A', tarfile.REGTYPE, 0o644, 0),
    ('xpdf-4.06/../A', tarfile.REGTYPE, 0o644, 0),
    ('xpdf-4.06//A', tarfile.REGTYPE, 0o644, 0),
    ('other/A', tarfile.REGTYPE, 0o644, 0),
    ('xpdf-4.06/A', tarfile.SYMTYPE, 0o644, 0),
    ('xpdf-4.06/A', tarfile.LNKTYPE, 0o644, 0),
    ('xpdf-4.06/A', tarfile.FIFOTYPE, 0o644, 0),
    ('xpdf-4.06/A', tarfile.CHRTYPE, 0o644, 0),
    ('xpdf-4.06/A', tarfile.REGTYPE, 0o4755, 0),
    ('xpdf-4.06/A', tarfile.REGTYPE, 0o644, 4 * 1024 * 1024 + 1),
])
def test_shared_archive_grammar_refuses_unsafe_or_excessive_members(monkeypatch, name, kind, mode, size):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w:gz') as archive:
        info = tarfile.TarInfo(name)
        info.type, info.mode, info.size = kind, mode, size
        info.linkname = '../TEST_ONLY-outside'
        archive.addfile(info, io.BytesIO(bytes(size)) if size else None)
    raw = stream.getvalue()
    monkeypatch.setattr(module, 'ARCHIVE_SHA256', hashlib.sha256(raw).hexdigest())
    with pytest.raises(ValueError, match='archive'):
        module.archive_files(raw)


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
