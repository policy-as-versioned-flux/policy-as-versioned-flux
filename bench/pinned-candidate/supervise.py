"""Foreground resource cage for one command and its own subprocesses.

This observer is distinct from the candidate actor. Requires psutil==7.1.3.
It never invokes a shell and never inspects or terminates unrelated processes.
"""
from __future__ import annotations

import json
from pathlib import Path
import platform
import subprocess
import time

import psutil


def _stop(child: subprocess.Popen, processes: list) -> None:
    for process in reversed(processes):
        try:
            process.terminate()
        except psutil.NoSuchProcess:
            pass
    if child.poll() is None:
        child.terminate()
    try:
        child.wait(timeout=2)
    except subprocess.TimeoutExpired:
        for process in reversed(processes):
            try:
                process.kill()
            except psutil.NoSuchProcess:
                pass
        if child.poll() is None:
            child.kill()
        child.wait(timeout=2)


def run(command: list[str], output: Path, *, rss_cap_bytes: int = 24*1024**3,
        timeout_seconds: float = 900) -> dict:
    """Capture and bound one foreground invocation; fail closed on missing RSS."""
    if not command or rss_cap_bytes <= 0 or timeout_seconds <= 0:
        raise ValueError('command and positive resource bounds required')
    output.mkdir(exist_ok=False)
    started = time.monotonic()
    peak = 0
    reason = None
    with (output / 'stdout').open('w') as stdout, (output / 'stderr').open('w') as stderr, \
            (output / 'resources.jsonl').open('w') as samples:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr)
        processes = []
        try:
            while child.poll() is None:
                observations = []
                try:
                    processes = [psutil.Process(child.pid), *psutil.Process(child.pid).children(recursive=True)]
                    total_rss = 0
                    for process in processes:
                        # Read and enforce RSS before optional CPU/thread observations.
                        # psutil.threads() is deliberately absent: it can need a Mac task port.
                        rss = process.memory_info().rss
                        total_rss += rss
                        observation: dict = {'pid': process.pid, 'rss_bytes': rss}
                        try:
                            observation['cpu_times'] = list(process.cpu_times())
                        except psutil.AccessDenied:
                            observation['cpu_times_error'] = 'AccessDenied'
                        observations.append(observation)
                    peak = max(peak, total_rss)
                    if total_rss > rss_cap_bytes:
                        reason = 'rss-cap'
                except psutil.NoSuchProcess:
                    if child.poll() is None:
                        # A short-lived helper may disappear between enumeration and read;
                        # retry promptly, without treating an absent sample as measured zero.
                        samples.write(json.dumps({'elapsed': time.monotonic()-started,
                                                  'observation': 'process-exited-during-sample'})+'\n')
                        samples.flush()
                except psutil.AccessDenied:
                    reason = 'rss-observation-denied'
                record: dict = {'elapsed': time.monotonic()-started, 'processes': observations}
                if platform.system() == 'Darwin' and child.poll() is None:
                    try:
                        threads = subprocess.run(['ps', '-M', '-p', str(child.pid), '-o', 'pid,%cpu,time'],
                                                 capture_output=True, text=True, timeout=2)
                        record['threads_ps'] = {'returncode': threads.returncode,
                                                'stdout': threads.stdout, 'stderr': threads.stderr}
                    except (OSError, subprocess.TimeoutExpired) as exc:
                        record['threads_ps_error'] = type(exc).__name__
                samples.write(json.dumps(record)+'\n')
                samples.flush()
                if time.monotonic()-started > timeout_seconds:
                    reason = 'timeout'
                if reason:
                    _stop(child, processes)
                    break
                time.sleep(0.1)
        finally:
            if child.poll() is None:
                _stop(child, processes)
        returncode = child.wait()
    result = {'command': command, 'child_pid': child.pid, 'returncode': returncode,
              'termination_reason': reason, 'wall_seconds': time.monotonic()-started,
              'peak_sampled_rss_bytes': peak, 'rss_cap_bytes': rss_cap_bytes,
              'timeout_seconds': timeout_seconds}
    (output / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main() -> None:
    import argparse
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rss-cap-mib', type=int, default=24576)
    parser.add_argument('--timeout-seconds', type=float, default=900)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    result = run(command, args.output, rss_cap_bytes=args.rss_cap_mib*1024**2,
                 timeout_seconds=args.timeout_seconds)
    print(json.dumps(result), flush=True)
    sys.exit(125 if result['termination_reason'] else result['returncode'])


if __name__ == '__main__':
    main()
