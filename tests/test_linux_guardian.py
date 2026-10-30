"""TEST_ONLY pure/external protocol controls. No helper/kernel/runtime execution."""
import importlib.util
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1]/'bench/pinned-candidate/linux_guardian.py'
spec = importlib.util.spec_from_file_location('linux_guardian_source_test', PATH)
assert spec is not None and spec.loader is not None
guardian = importlib.util.module_from_spec(spec)
if PATH.exists(): spec.loader.exec_module(guardian)

class GuardianProtocolTests(unittest.TestCase):
    def test_fragmented_external_child_bytes_cannot_mint_host_events(self):
        reader = guardian.FrameReader(64, 256)
        self.assertEqual(reader.feed(b'{"event":"done"'), [])
        packets = reader.feed(b',"lease":"fake"}\n')
        writer = guardian.Wire('a'*48)
        wrapped = writer.frame('preflight', packets[0])
        self.assertEqual(json.loads(wrapped), {'event':'frame','lease':'a'*48,
            'phase':'preflight','body':{'event':'done','lease':'fake'}})
        reader.eof()
        reader.feed(b"{\"unfinished\":")
        with self.assertRaises(ValueError): reader.eof()

    def test_external_mount_snapshot_cannot_hide_writable_alias_or_host_proc(self):
        fixture = ('1 0 0:1 / / ro,nosuid,nodev - tmpfs tmpfs ro\n'
            '2 1 0:2 / /proc ro,nosuid,nodev,noexec - proc proc ro\n'
            '3 1 0:3 / /attempt rw,nosuid,nodev,noexec - tmpfs tmpfs rw,size=131072k\n'
            '4 1 8:1 /snapshot/python /python ro,nosuid,nodev - ext4 /dev/test ro\n')
        self.assertEqual(guardian.inspect_mounts(fixture, {'/python'})['root_readonly'], True)
        with self.assertRaisesRegex(ValueError, 'writable'):
            guardian.inspect_mounts(fixture.replace('/python ro,nosuid', '/python rw,nosuid'), {'/python'})
        with self.assertRaisesRegex(ValueError, 'undeclared'):
            guardian.inspect_mounts(fixture+'5 1 0:4 / /host ro - proc proc ro\n', {'/python'})

    def test_closed_request_rejects_path_authority_and_wrong_identity_type(self):
        fixture = {'authority':'a'*64,'profile_sha256':'b'*64,
            'request':{'input':{'TEST_ONLY':'arbitrary'},'prompt_utf8':'TEST_ONLY prompt'},
            'supervisor_pid':17,'supervisor_start':'42','deadline_monotonic':10000.}
        self.assertEqual(guardian.validate_request(fixture), fixture)
        for extra in ('command','candidate_uid','cgroup_parent'):
            with self.assertRaises(ValueError): guardian.validate_request(dict(fixture, **{extra:'/TEST_ONLY'}))
        with self.assertRaises(ValueError): guardian.validate_request(dict(fixture, supervisor_pid=True))
        with self.assertRaises(ValueError): guardian.validate_request(dict(fixture,
            request=dict(fixture['request'],expected_label='TEST_ONLY forbidden extra')))

    def test_kernel_resource_snapshot_requires_exact_quota_cpuset_swap_and_reserve(self):
        fixture = {'limits':{'memory.max':'12884901888','memory.swap.max':'0','pids.max':'128',
            'cpu.max':'200000 100000','cpu.max.burst':'0','cpuset.cpus.effective':'2,4',
            'cpuset.mems.effective':'0'}, 'memory.current':100, 'memory.peak':200,
            'memory.swap.current':0,'pids.current':1,'memory.events':{'max':0,'oom':0,'oom_kill':0},
            'reserve':{'memory_available':3000000000,'disk_free':6000000000}}
        guardian.validate_resources(fixture, {2,4})
        for changed in ({'memory.swap.current':1}, {'pids.current':129},
                {'limits':dict(fixture['limits'], **{'cpuset.cpus.effective':'2-4'})},
                {'limits':dict(fixture['limits'], **{'cpu.max':'max 100000'})},
                {'memory.events':{'oom_kill':1}},
                {'reserve':{'memory_available':100,'disk_free':6000000000}}):
            with self.assertRaises(ValueError): guardian.validate_resources(dict(fixture, **changed), {2,4})

    def test_teardown_receipt_requires_all_actual_kernel_witnesses(self):
        self.assertEqual(guardian.teardown_receipt(False, True, True, True),
            {'empty':True,'reaped':True,'removed':True})
        for witnesses in ((True,True,True,True),(False,False,True,True),
                (False,True,False,True),(False,True,True,False),(0,True,True,True)):
            with self.assertRaises(ValueError): guardian.teardown_receipt(*witnesses)

    def test_external_journal_rejects_fragment_overflow_and_keeps_terminal_capacity(self):
        reader=guardian.FrameReader(16,40)
        with self.assertRaisesRegex(ValueError, 'frame'):
            reader.feed(b'1234567890123456')
        reader=guardian.FrameReader(16,20)
        self.assertEqual(reader.feed(b'{}\n{}\n{}\n{}\n{}\n{}\n'), [{}]*6)
        with self.assertRaisesRegex(ValueError, 'journal'):reader.feed(b'{}\n')
        wire=guardian.Wire('a'*48)
        wire.total=guardian.MAX_STDOUT-32768
        with self.assertRaises(ValueError):wire.frame('generate',{'type':'token','index':0,'id':7})
        self.assertEqual(json.loads(wire.event('failure',error='TEST_ONLY overflow'))['event'],'failure')

    def test_protected_profile_cannot_widen_reviewed_numerical_or_decode_settings(self):
        config={'profile':'signal-linux-bf16-v1','max_input_tokens':4096,'max_new_tokens':512,
            'threads':2,'interop_threads':1,'timeout_seconds':900,
            'linux_profile':{'model_id':'Qwen/Qwen3-4B-Instruct-2507',
                'revision':'cdbee75f17c01a7cc42f958dc650907174af0554',
                'model_manifest_sha256':'409410d7d41d7e62aafb27c18f049fe3c62d66383b3a5b89d5fadfd3b773fd7e',
                'chat_template_sha256':'64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326',
                'runtime_manifest_sha256':'a'*64,'dtype':'torch.bfloat16','device':'cpu','attention':'eager',
                'do_sample':False,'num_beams':1,'num_return_sequences':1,'seed':0,'use_cache':True,
                'cache_implementation':'dynamic','eos_token_ids':[151645,151643],'pad_token_id':151643}}
        guardian.validate_reviewed_profile(config)
        for changed in ({'max_new_tokens':513},{'threads':True},{'timeout_seconds':901},
                {'context_tokens':8192},{'linux_profile':dict(config['linux_profile'],device='cuda')}):
            with self.assertRaises(ValueError): guardian.validate_reviewed_profile(dict(config,**changed))


def test_shared_parent_deadline_cannot_reset_after_privileged_setup_or_widen_profile():
    assert guardian.attempt_deadlines(1000.,900,1050.) == (1040.,1050.)
    assert guardian.attempt_deadlines(1000.,900,3000.) == (1890.,1900.)
    for deadline in (999.,1005.,float('nan'),float('inf'),True,'1050'):
        with unittest.TestCase().assertRaises(ValueError):
            guardian.attempt_deadlines(1000.,900,deadline)
