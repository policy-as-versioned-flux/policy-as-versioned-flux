"""Exercise kernel controls in disposable children; never install a filter in pytest."""
import importlib.util
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import unittest

PATH = Path(__file__).with_name('linux_network.py')
spec = importlib.util.spec_from_file_location('linux_network', PATH)
assert spec is not None and spec.loader is not None
network = importlib.util.module_from_spec(spec)
spec.loader.exec_module(network)
UNPRIVILEGED_LINUX = sys.platform == 'linux' and os.geteuid() != 0


class LinuxNetworkTests(unittest.TestCase):
    @unittest.skipIf(sys.platform == 'linux', 'the real non-Linux refusal control')
    def test_an_actual_non_linux_host_is_refused(self):
        with self.assertRaisesRegex(RuntimeError, 'Linux'):
            network.install_network_denial()

    @unittest.skipUnless(UNPRIVILEGED_LINUX, 'requires an unprivileged actual Linux child')
    def test_real_kernel_denies_network_and_exec_child_inherits_it(self):
        result = subprocess.run([sys.executable, '-I', str(PATH), '--control'],
                                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        print(result.stdout.strip(), flush=True)  # retain actual kernel observations in CI logs
        record = json.loads(result.stdout)
        self.assertEqual(record['state']['NoNewPrivs'], '1')
        self.assertEqual(record['state']['Seccomp'], '2')
        for observed in (record['probes'], record['exec_child']['probes']):
            self.assertEqual(len(observed), 8)
            self.assertTrue(all(row['errno'] == 1 for row in observed), observed)
        self.assertEqual(record['exec_child']['state']['NoNewPrivs'], '1')

    @unittest.skipUnless(UNPRIVILEGED_LINUX, 'requires an unprivileged actual Linux child')
    def test_a_preexisting_socket_refuses_installation(self):
        script = ('import runpy,socket; m=runpy.run_path(' + repr(str(PATH)) + '); '
                  's=socket.socket(); '
                  '\ntry: m["install_network_denial"]()'
                  '\nexcept RuntimeError as e: print(e)'
                  '\nelse: raise AssertionError("inherited socket accepted")')
        result = subprocess.run([sys.executable, '-I', '-c', script],
                                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                timeout=10, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('socket', result.stdout)

    @unittest.skipUnless(UNPRIVILEGED_LINUX and platform.machine() == 'x86_64',
                         'requires actual unprivileged x86_64 Linux')
    def test_x32_syscall_aliases_refuse_in_disposable_children(self):
        for number in (0x40000000 | 41, 512):
            script = ('import ctypes,resource,runpy; '
                      'resource.setrlimit(resource.RLIMIT_CORE,(0,0)); '
                      'm=runpy.run_path(' + repr(str(PATH)) + '); '
                      'm["install_network_denial"](); '
                      'ctypes.CDLL(None).syscall(ctypes.c_long(' + str(number) + '),2,1,0); '
                      'raise SystemExit(99)')
            result = subprocess.run([sys.executable, '-I', '-c', script],
                                    stdin=subprocess.DEVNULL, capture_output=True, timeout=10,
                                    check=False)
            self.assertEqual(result.returncode, -signal.SIGSYS, (number, result.stderr))


if __name__ == '__main__':
    unittest.main()
