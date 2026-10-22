"""Narrow live measurement; no credential bytes or remote writes are emitted."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name('actor142-stream')
OUT.mkdir(exist_ok=True)
PYTHON = ROOT / '.venv/bin/python'


def measure():
    rebuilt = dict(os.environ)
    for key in tuple(rebuilt):
        if key.startswith(('GIT_', 'GH_', 'GITHUB_')) or key in ('SSH_AUTH_SOCK', 'SSH_AGENT_PID'):
            rebuilt.pop(key)
    rebuilt['GIT_TERMINAL_PROMPT'] = '0'
    rebuilt['GCM_INTERACTIVE'] = 'never'
    result = {}
    for label, path in [('owner_gitconfig', Path.home() / '.gitconfig'),
                        ('positive_control', OUT / 'readable-control.txt')]:
        try:
            with path.open('rb') as handle:
                handle.read(1)
            result[label] = {'readable': True}
        except OSError as exc:
            result[label] = {'readable': False, 'errno': exc.errno}
    for label, args in [
        ('rebuilt_keychain_route', ['gh', 'auth', 'token']),
        ('rebuilt_public_git_network', ['git', '-c', 'credential.helper=', '-c',
          'credential.interactive=false', 'ls-remote',
          'https://github.com/policy-as-versioned-flux/policy-as-versioned-flux.git', 'HEAD'])]:
        try:
            proc = subprocess.run(args, env=rebuilt, capture_output=True, timeout=12)
            # Output stays only in this process's memory. Never write token material.
            result[label] = {'exit': proc.returncode, 'nonempty_output': bool(proc.stdout.strip())}
            del proc
        except subprocess.TimeoutExpired:
            result[label] = {'timed_out': True}
    result['at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    print(json.dumps(result, sort_keys=True))


if '--measure' in sys.argv:
    measure()
    raise SystemExit(0)

(OUT / 'readable-control.txt').write_text('nonsecret measurement control\n')
(OUT / 'unit').mkdir(exist_ok=True)
source = (ROOT / 'talk/local-clock.sh').read_text()
function = source[source.index('make_cage() {'):source.index('cage_config_changed() {')]
env = dict(os.environ, HUB=str(ROOT), PY=str(PYTHON), RUN_DIR=str(OUT), RUN_ID='actor142-measurement')
subprocess.run(['bash', '-c', function + '\ntag=live\nmake_cage live "$RUN_DIR/unit" "$RUN_DIR/unit"'],
               env=env, check=True, capture_output=True)
cage = OUT / 'live.cage'
for key in ('CLAUDECODE', 'CLAUDE_CODE_CHILD_SESSION', 'SSH_AUTH_SOCK', 'SSH_AGENT_PID',
            'GITHUB_TOKEN', 'GH_ENTERPRISE_TOKEN', 'GITHUB_ENTERPRISE_TOKEN', 'GIT_ASKPASS',
            'SSH_ASKPASS', 'GIT_CONFIG_PARAMETERS', 'GIT_DIR', 'GIT_WORK_TREE'):
    env.pop(key, None)
env.update(GH_TOKEN='local-clock-no-push-capability', GH_CONFIG_DIR=str(cage / 'no-gh'),
           GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=str(cage / 'gitconfig'),
           GIT_TERMINAL_PROMPT='0', GIT_EXEC_PATH=str(cage / 'no-git-core'), GIT_ALLOW_PROTOCOL='none',
           GIT_SSH_COMMAND=str(cage / 'no-ssh.sh'), TWIN_ENACT_MODE='operations',
           GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='commit.gpgsign', GIT_CONFIG_VALUE_0='false',
           GIT_CONFIG_KEY_1='tag.gpgsign', GIT_CONFIG_VALUE_1='false')
command = f"git -c alias.capability-probe='!{PYTHON} {Path(__file__).resolve()} --measure' capability-probe"
prompt = ('Run exactly this one Bash command once, then report its JSON verbatim. '
          'This is an owner-authorized, read-only capability measurement. Do not inspect other files, '
          'edit any file, retry without sandbox, or perform any other operation. Command: ' + command)
args = ['claude', '-p', prompt, '--max-turns', '4', '--output-format', 'stream-json', '--verbose',
        '--restricted', '--tools', 'Bash,Read,Edit,Write,Glob,Grep', '--strict-mcp-config',
        '--mcp-config', str(cage / 'mcp.json'), '--settings', str(cage / 'settings.json'),
        '--permission-mode', 'acceptEdits', '--allowedTools', 'Bash(git *)',
        '--disallowedTools', 'Task,WebFetch,WebSearch,NotebookEdit,Bash(gh *),Bash(security *)',
        '--no-session-persistence', '--add-dir', str(OUT / 'unit')]
(OUT / 'INVOCATION.json').write_text(json.dumps({'at': dt.datetime.now(dt.timezone.utc).isoformat(),
    'argv': args, 'settings_sha256': hashlib.sha256((cage / 'settings.json').read_bytes()).hexdigest(),
    'source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'remote_mutations': False}, indent=2)+'\n')
with (OUT / 'claude-result.jsonl').open('wb') as stdout, (OUT / 'claude-stderr.txt').open('wb') as stderr:
    proc = subprocess.Popen(args, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL,
                            start_new_session=True)
    try:
        code = proc.wait(timeout=180)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        code = proc.wait(timeout=10)
(OUT / 'EXIT.json').write_text(json.dumps({'exit':code})+'\n')
print(json.dumps({'exit':code, 'result_file':str(OUT / 'claude-result.jsonl')}))
