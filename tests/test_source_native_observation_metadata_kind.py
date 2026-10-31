"""Public synthetic metadata-kind consistency; no OS/backend or child is invoked."""
import pytest
from twin import source_native_observation as n
from test_source_native_observation import fixture, splice, call, blob, sidecar_run
from test_source_native_observation_repairs import stat_buffer


@pytest.mark.parametrize('fd', [0, 1, 2])
@pytest.mark.parametrize('mode', [0o020666, 0o100444])
def test_known_owned_stdio_cannot_replay_a_non_fifo_stat(fd, mode):
    observation, archive = fixture()
    identity = [2, 20 + fd, mode, 1000, 1000, 1, 0, 1, 1]
    splice(observation, call(5, [fd, 8192], detail={
        'buffer_sha256': blob(archive, stat_buffer(identity))}))
    with pytest.raises(ValueError, match='kind|type'):
        n.verify_native_observation(observation, archive, purpose='TEST_ONLY')


@pytest.mark.parametrize('fd', [0, 1, 2])
def test_known_owned_stdio_retains_valid_fifo_stat(fd):
    observation, archive = fixture()
    identity = [2, 20 + fd, 0o010600, 1000, 1000, 1, 0, 1, 1]
    splice(observation, call(5, [fd, 8192], detail={
        'buffer_sha256': blob(archive, stat_buffer(identity))}))
    assert n.verify_native_observation(observation, archive, purpose='TEST_ONLY')['stdout_bytes'] == 6


def test_owned_stdio_alias_cannot_change_stat_kind():
    observation, archive = fixture()
    identity = [2, 21, 0o100444, 1000, 1000, 1, 0, 1, 1]
    request = call(32, [1], result=3)
    request += call(5, [3, 8192], detail={'buffer_sha256': blob(archive, stat_buffer(identity))})
    request += call(3, [3])
    splice(observation, request)
    with pytest.raises(ValueError, match='kind|type'):
        n.verify_native_observation(observation, archive, purpose='TEST_ONLY')


@pytest.mark.parametrize('kind', ['file', 'directory'])
def test_known_regular_and_directory_descriptor_stat_stays_valid(kind):
    observation, archive = fixture()
    if kind == 'file':
        path, flags = '/data', 0x80000
        identity = observation['files'][path]['identity']
    else:
        path, flags = '/', 0x90000
        identity = [1, 123, 0o40555, 1000, 1000, 1, 0, 1, 1]
    request = call(2, [0, flags], {'path': path}, 3, {'kind': kind, 'identity': identity})
    request += call(5, [3, 8192], detail={'buffer_sha256': blob(archive, stat_buffer(identity))})
    request += call(3, [3])
    splice(observation, request)
    assert n.verify_native_observation(observation, archive, purpose='TEST_ONLY')['stdout_bytes'] == 6


def sidecar_stat(mutation=None):
    observation, archive = sidecar_run()
    identity = [3, 30, 0o100600, 1000, 1000, 1, 2, 7000000003, 9000000004]
    if mutation is not None:
        field, value = mutation
        identity[field] = value
    # The first sidecar has already received its two bytes; its fixed creation
    # mode/ownership/link facts stay known while its size and times can change.
    close = next(i for i, event in enumerate(observation['events'])
                 if event['kind'] == 'enter' and event['data']['nr'] == 3)
    inserted = [{'seq': 0, 'at_ns': 0, 'kind': kind, 'data': data}
                for kind, data in call(5, [3, 8192], detail={
                    'buffer_sha256': blob(archive, stat_buffer(identity))})]
    observation['events'][close:close] = inserted
    for i, event in enumerate(observation['events']):
        event['seq'], event['at_ns'] = i, i * 1000
    return observation, archive


def test_sidecar_stat_preserves_owned_writes_without_freezing_mutable_size_or_times():
    observation, archive = sidecar_stat()
    assert n.verify_native_observation(observation, archive, purpose='TEST_ONLY')['stdout_bytes'] == 6


@pytest.mark.parametrize('field,value', [(2, 0o020600), (2, 0o100644), (3, 1001), (4, 1001), (5, 2)])
def test_sidecar_stat_cannot_change_known_fixed_creation_facts(field, value):
    observation, archive = sidecar_stat((field, value))
    with pytest.raises(ValueError, match='identity|kind'):
        n.verify_native_observation(observation, archive, purpose='TEST_ONLY')


@pytest.mark.parametrize('mode', [0o020666, 0o100444, 0o40555])
def test_unknown_path_stat_does_not_invent_an_unobserved_inode_kind(mode):
    observation, archive = fixture()
    identity = [8, 800, mode, 2000, 2000, 1, 0, 1, 1]
    splice(observation, call(4, [4096, 8192], {'path': '/bin/unretained-metadata'},
                            detail={'buffer_sha256': blob(archive, stat_buffer(identity))}))
    assert n.verify_native_observation(observation, archive, purpose='TEST_ONLY')['stdout_bytes'] == 6


def test_original_pipe_stat_does_not_invent_unrecorded_permission_or_owner_facts():
    observation, archive = fixture()
    identity = [2, 21, 0o010666, 2000, 2000, 1, 0, 1, 1]
    splice(observation, call(5, [1, 8192], detail={
        'buffer_sha256': blob(archive, stat_buffer(identity))}))
    assert n.verify_native_observation(observation, archive, purpose='TEST_ONLY')['stdout_bytes'] == 6
