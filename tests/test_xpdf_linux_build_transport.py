"""Fixed HTTPS parser and CLI tests with memory-only sockets; never connect."""
from email.message import Message
import io
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_xpdf_linux_build import module, held_bundle, encoded, sha
from test_xpdf_linux_build_model import retained_archive


def fetch_model(monkeypatch, wire, tmp_path):
    calls, diagnostics = [], io.BytesIO()
    class Socket:
        def makefile(self, *args): return io.BytesIO(wire)
    class Connection:
        def __init__(self, host, **kwargs): calls.append(('connect', host, kwargs['timeout']))
        def request(self, method, path, **kwargs): calls.append(('request', method, path, kwargs['headers']))
        def getresponse(self):
            response = self.response_class(Socket(), method='GET')
            response.begin()
            return response
        def close(self): calls.append(('closed',))
    monkeypatch.setattr(module.http.client, 'HTTPSConnection', Connection)
    monkeypatch.setattr(module.ssl, 'create_default_context', lambda **kwargs: object())
    monkeypatch.setattr(module, 'sys', SimpleNamespace(stderr=SimpleNamespace(buffer=diagnostics)))
    ca_file = tmp_path / 'TEST_ONLY-CA.data'
    ca_file.write_bytes(b'TEST_ONLY CA bytes, never passed to a real TLS context')
    monkeypatch.setattr(module, '_APPOINTED_EXECUTION', {'source_transport': {'selection_sha256': 'e' * 64, 'ssl_files': {str(ca_file): sha(ca_file.read_bytes())}, 'ca_file': str(ca_file)}})
    return calls, diagnostics


def test_fixed_fetch_only_accepts_exact_retained_archive_and_literal_route(monkeypatch, tmp_path):
    raw = retained_archive()
    calls, _ = fetch_model(monkeypatch, b'HTTP/1.1 200 OK\r\nContent-Length: 999317\r\n\r\n' + raw, tmp_path)
    output = io.BytesIO()
    module._fixed_fetch(output)
    assert output.getvalue() == raw
    assert calls == [('connect', 'dl.xpdfreader.com', 25), ('request', 'GET', '/xpdf-4.06.tar.gz', {'Accept-Encoding': 'identity'}), ('closed',)]


@pytest.mark.parametrize('wire', [
    b'HTTP/1.1 302 Redirect\r\nLocation: https://TEST_ONLY.invalid/alternate\r\n\r\n',
    b'HTTP/1.1 100 Continue\r\n\r\nHTTP/1.1 200 OK\r\n\r\n',
    b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n\r\nA',
    b'HTTP/1.1 200 OK\r\nX: ' + b'A' * 32768 + b'\r\n\r\n',
    b'HTTP/1.1 200 OK\r\nContent-Length: 1\r\n\r\nA',
])
def test_fixed_fetch_preserves_failure_without_redirect_or_retry(monkeypatch, wire, tmp_path):
    calls, _ = fetch_model(monkeypatch, wire, tmp_path)
    output = io.BytesIO()
    with pytest.raises((module.BuildHold, module.http.client.HTTPException)):
        module._fixed_fetch(output)
    assert sum(call[0] == 'connect' for call in calls) == 1 and calls[-1] == ('closed',)


def test_fixed_fetch_caps_overflow_prefix_and_records_observed_lower_bound(monkeypatch, tmp_path):
    calls, diagnostics = fetch_model(monkeypatch, b'HTTP/1.1 200 OK\r\nContent-Length: 999318\r\n\r\n' + b'A' * 999318, tmp_path)
    output = io.BytesIO()
    with pytest.raises(module.BuildHold): module._fixed_fetch(output)
    assert len(output.getvalue()) == 999317
    assert b'"observed_body_bytes_lower_bound":999318' in diagnostics.getvalue()
    assert b'"body_overflow":true' in diagnostics.getvalue()
    assert calls[-1] == ('closed',)


def test_internal_cli_cannot_enable_transport_without_private_appointment(monkeypatch):
    output, error = io.BytesIO(), io.BytesIO()
    monkeypatch.setattr(module, 'sys', SimpleNamespace(stdout=SimpleNamespace(buffer=output), stderr=SimpleNamespace(buffer=error)))
    monkeypatch.setattr(module.http.client, 'HTTPSConnection', lambda *a, **k: pytest.fail('no network'))
    assert module.main(['--internal-fetch']) == 2
    assert output.getvalue() == b'' and b'not appointed' in error.getvalue()


def test_build_cli_is_held_and_has_no_public_enable_option(monkeypatch, tmp_path):
    output = io.BytesIO()
    monkeypatch.setattr(module, 'sys', SimpleNamespace(stdout=SimpleNamespace(buffer=output)))
    selection = tmp_path / 'SELECTION.json'
    selection.write_bytes(held_bundle()[0]['SELECTION.json'])
    assert module.main(['--build', str(selection), str(tmp_path / 'not-created')]) == 2
    assert not (tmp_path / 'not-created').exists()
    assert b'"status":"HELD"' in output.getvalue()


def test_unknown_cleanup_failure_prefix_is_truthful_and_bounded(tmp_path):
    import json
    _, result = held_bundle()
    root = tmp_path / 'owned'
    root.mkdir()
    (root / 'journal').mkdir()
    body = b'A' * (16 * 1024 * 1024)
    result['commands'] = [{'stdout': {'sha256': sha(body), 'retained_bytes': len(body), 'observed_bytes_lower_bound': len(body), 'state': 'COMPLETE'},
                           'stderr': {'sha256': sha(b''), 'retained_bytes': 0, 'observed_bytes_lower_bound': 0, 'state': 'COMPLETE'}}]
    module._retain_failure(root, result, {'journal/000-stdout.log': (body, 'raw-log'), 'journal/000-stderr.log': (b'', 'raw-log')})
    record = json.loads((root / 'FIRST-FAILURE.json').read_bytes())['commands'][0]['stdout']
    assert record['state'] == 'PREFIX_ONLY' and record['retained_bytes'] == 15 * 1024 * 1024
    assert record['observed_bytes_lower_bound'] == 16 * 1024 * 1024
    assert sum(p.stat().st_size for p in root.rglob('*') if p.is_file()) < 16 * 1024 * 1024


def test_failure_retention_refuses_a_symlinked_parent(tmp_path):
    root, outside = tmp_path / 'owned', tmp_path / 'outside'
    root.mkdir(); outside.mkdir()
    (root / 'journal').symlink_to(outside, target_is_directory=True)
    _, result = held_bundle()
    module._retain_failure(root, result, {'journal/000-stdout.log': (b'TEST_ONLY first failure', 'raw-log')})
    assert list(outside.iterdir()) == []
