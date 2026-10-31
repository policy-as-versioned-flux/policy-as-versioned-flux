#!/usr/bin/env python3
"""Explicitly authorized synthetic recorder only; never invokes or imports Xpdf."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


def run(executable: Path, expected_sha256: str, destination: Path) -> None:
    if executable.is_symlink() or hashlib.sha256(executable.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('TEST_ONLY executable identity differs')
    if os.path.lexists(destination):
        raise FileExistsError(destination)
    destination.mkdir(mode=0o700)
    read_fd, write_fd = os.pipe()
    started = time.monotonic()
    process = None
    streams = {'stdout': bytearray(), 'stderr': bytearray(), 'origin': bytearray()}
    caps = {'stdout': 16384, 'stderr': 8192, 'origin': 65536}
    error = None
    eofs = set()
    cleanup_error = None
    selection = selectors.DefaultSelector()
    try:
        process = subprocess.Popen([str(executable.resolve()), str(write_fd)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC'}, pass_fds=(write_fd,),
            start_new_session=True)
        os.close(write_fd);write_fd = -1
        assert process.stdout is not None and process.stderr is not None
        for source, name in ((process.stdout,'stdout'), (process.stderr,'stderr'), (read_fd,'origin')):
            os.set_blocking(source if isinstance(source,int) else source.fileno(), False)
            selection.register(source,selectors.EVENT_READ,name)
        while selection.get_map():
            if time.monotonic()-started>5:
                raise TimeoutError('TEST_ONLY original five-second deadline')
            for key,_ in selection.select(0.05):
                fd=key.fileobj if isinstance(key.fileobj,int) else key.fileobj.fileno()
                try: raw=os.read(fd,4096)
                except BlockingIOError: continue
                if not raw:
                    eofs.add(key.data);selection.unregister(key.fileobj);continue
                name=key.data
                if len(streams[name])+len(raw)>caps[name]:
                    raise ValueError('TEST_ONLY stream cap exceeded: '+name)
                streams[name].extend(raw)
        process.wait(timeout=max(0.001,5-(time.monotonic()-started)))
    except BaseException as failure:
        error=type(failure).__name__+': '+str(failure)
    finally:
        if process is not None and process.poll() is None:
            try:
                try: os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError: pass
                try: process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    try: os.killpg(process.pid,signal.SIGKILL)
                    except ProcessLookupError: pass
                    process.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired) as failure:
                cleanup_error=type(failure).__name__+': '+str(failure)
        selection.close()
        os.close(read_fd)
        if write_fd>=0: os.close(write_fd)
        if process is not None:
            if process.stdout is not None: process.stdout.close()
            if process.stderr is not None: process.stderr.close()
        for name,raw in streams.items():
            with os.fdopen(os.open(destination/(name+'.bin'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as stream: stream.write(raw)
        result={'scope':'TEST_ONLY authored recorder; no converter/PDF/native observer or actual authority',
            'executable_sha256':expected_sha256,'actual_returncode':None if process is None else process.returncode,
            'elapsed_seconds':time.monotonic()-started,'error':error,'stream_caps':caps,
            'streams':{name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
                       for name,raw in streams.items()},'one_original_deadline_seconds':5,
            'eof_observed':{name:name in eofs for name in streams},
            'cleanup':{'child_terminal_reaped':process is not None and process.returncode is not None,
                       'owned_stream_descriptors_closed':True,'error':cleanup_error}}
        with os.fdopen(os.open(destination/'RESULT.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as record: json.dump(result,record,indent=2,sort_keys=True);record.write('\n')
    if error or cleanup_error or eofs!=set(streams) or process is None or process.returncode!=0:
        raise ValueError('TEST_ONLY recorder did not complete; see owned RESULT.json')
    if bytes(streams['stdout'])!=b'AB\nAB\n))\nS\nX\n\xc3\xa9\nba\nZY\n' or streams['stderr']:
        raise ValueError('TEST_ONLY output differs from independently fixed literal')


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable',type=Path)
    parser.add_argument('expected_sha256')
    parser.add_argument('new_owned_destination',type=Path)
    args=parser.parse_args();run(args.executable,args.expected_sha256,args.new_owned_destination)


if __name__=='__main__': main()
