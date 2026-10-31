"""Pure OS models: restoration faults cannot replace the original cancellation."""
import json

import pytest

from test_xpdf_linux_build import module
from test_xpdf_linux_build_model import retained_archive, whole_model


def failed_restoration(monkeypatch):
    calls = []
    def modeled_umask(value):
        calls.append(value)
        if len(calls) == 1:
            assert value == 0o077
            return 0o022
        raise SystemExit('TEST_ONLY secondary umask restoration failure')
    monkeypatch.setattr(module.os, 'umask', modeled_umask)
    return calls


def test_original_cancellation_survives_secondary_restoration_failure(monkeypatch, tmp_path):
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive())
    original = KeyboardInterrupt('TEST_ONLY original launch cancellation')
    def interrupted_launch(*args, **kwargs):
        raise original
    monkeypatch.setattr(module.subprocess, 'Popen', interrupted_launch)
    masks = failed_restoration(monkeypatch)
    with pytest.raises(KeyboardInterrupt) as raised:
        module.build_linux_pair(selection, root)
    assert raised.value is original
    assert masks == [0o077, 0o022]
    first = json.loads((root / 'FIRST-FAILURE.json').read_bytes())
    assert first['first_failure']['reason'] == 'original interruption; workspace retained'
    fault = json.loads((root / 'UMASK-RESTORE-FAULT.json').read_bytes())
    assert fault['restoration'] == 'UNOBSERVED'
    assert fault['secondary_type'] == 'SystemExit' and fault['original_type'] == 'KeyboardInterrupt'
    assert fault['first_failure'] == first['first_failure']
    assert (root / 'UMASK-RESTORE-FAULT.json').stat().st_size < 8192
    assert root.exists() and not (root / 'export/RESULT.json').exists()


@pytest.mark.parametrize('prior_failure', [False, True])
def test_restoration_failure_without_pending_cancellation_cannot_return_success(monkeypatch, tmp_path, prior_failure):
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive(), fail_stage='cmake' if prior_failure else None)
    masks = failed_restoration(monkeypatch)
    with pytest.raises(SystemExit, match='secondary umask restoration failure'):
        module.build_linux_pair(selection, root)
    assert masks == [0o077, 0o022]
    first = json.loads((root / 'FIRST-FAILURE.json').read_bytes())
    fault = json.loads((root / 'UMASK-RESTORE-FAULT.json').read_bytes())
    assert first['status'] == 'HELD' and first['files_manifest_sha256'] is None
    assert fault['restoration'] == 'UNOBSERVED' and fault['original_type'] is None
    assert fault['first_failure'] == first['first_failure']
    if prior_failure:
        assert first['first_failure']['phase'] == 'pristine'
        assert first['first_failure']['reason'] != 'umask restoration unobserved; workspace retained'
        assert fault['export_terminal'] == 'NOT_OBSERVED'
    else:
        assert first['first_failure']['reason'] == 'umask restoration unobserved; workspace retained'
        assert fault['export_terminal'] == 'RENAMED_INCOMPLETE'
        assert (root / 'export/RESULT-INCOMPLETE.json').exists()
    assert root.exists() and not (root / 'export/RESULT.json').exists()


def test_fault_evidence_interruption_still_cannot_replace_original_cancellation(monkeypatch, tmp_path):
    selection, root, _ = whole_model(monkeypatch, tmp_path, retained_archive())
    original = KeyboardInterrupt('TEST_ONLY original launch cancellation')
    def interrupted_launch(*args, **kwargs):
        raise original
    monkeypatch.setattr(module.subprocess, 'Popen', interrupted_launch)
    failed_restoration(monkeypatch)
    original_open = module.os.open
    def interrupted_evidence(path, *args, **kwargs):
        if path == 'UMASK-RESTORE-FAULT.json':
            raise SystemExit('TEST_ONLY tertiary evidence interruption')
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(module.os, 'open', interrupted_evidence)
    with pytest.raises(KeyboardInterrupt) as raised:
        module.build_linux_pair(selection, root)
    assert raised.value is original
    assert root.exists() and (root / 'FIRST-FAILURE.json').exists()
    assert not (root / 'UMASK-RESTORE-FAULT.json').exists()
    assert not (root / 'export/RESULT.json').exists()
