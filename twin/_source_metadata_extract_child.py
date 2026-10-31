"""Fixed isolated text/HTML child. No repository imports, site, models or network.

Invoked by source_metadata_migration with -I -S -B and a fresh pycache prefix.
The preflight loads these same imports before any source data is read.
"""
import hashlib
import html.parser
import json
import os
from pathlib import Path
import sys


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def runtime_files():
    paths = {str(Path(sys.executable).resolve()), str(Path(__file__).resolve())}
    for module in tuple(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_file():
            paths.add(str(Path(path).resolve()))
    return {'schema': 'twin.source-extraction-process-files/v1', 'python': sys.version,
        'executable': str(Path(sys.executable).resolve()),
        'files': [{'path': p, 'sha256': hashlib.sha256(Path(p).read_bytes()).hexdigest(),
                   'bytes': Path(p).stat().st_size} for p in sorted(paths)]}


class Emitter(html.parser.HTMLParser):
    def __init__(self, syntax, output_limit, syntax_limit):
        super().__init__(convert_charrefs=True)
        self.syntax, self.output_limit, self.syntax_limit = syntax, output_limit, syntax_limit
        self.cursor, self.syntax_bytes, self.ordinal = 0, 0, 0

    def emit(self, text, event=None):
        raw = text.encode('utf-8')
        end = self.cursor + len(raw)
        if end > self.output_limit:
            raise ValueError('output-limit')
        if event:
            line = canonical({'start_byte': self.cursor, 'end_byte': end,
                'kind': 'syntactic-separator', 'text_utf8': text,
                'event_ordinal': self.ordinal, 'event_kind': event}) + b'\n'
            if self.syntax_bytes + len(line) > self.syntax_limit:
                raise ValueError('syntax-limit')
            self.syntax.write(line)
            self.syntax_bytes += len(line)
            self.ordinal += 1
        sys.stdout.buffer.write(raw)
        self.cursor = end

    def handle_data(self, text):
        self.emit(text)

    def handle_starttag(self, tag, attrs):
        self.emit('\n', 'start')

    def handle_endtag(self, tag):
        self.emit('\n', 'end')

    def handle_startendtag(self, tag, attrs):
        self.emit('\n', 'startend')


def main():
    if sys.argv[1:] == ['--inventory']:
        sys.stdout.buffer.write(canonical(runtime_files()))
        return 0
    if len(sys.argv) != 6 or sys.argv[1] != '--run':
        return 2
    _, _, input_path, config_path, syntax_path, runtime_path, = sys.argv
    config = json.loads(Path(config_path).read_bytes())
    # Capture before and after: source data cannot add undeclared imports/resources.
    before = runtime_files()
    os.umask(0o077)
    fd = os.open(runtime_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'wb') as runtime:
        runtime.write(canonical(before))
    raw = Path(input_path).read_bytes()
    if len(raw) > config['limits']['input_bytes']:
        raise ValueError('input-limit')
    text = raw.decode('utf-8', errors='strict')
    fd = os.open(syntax_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'wb') as syntax:
        if config['profile'] == 'utf8-identity/1':
            sys.stdout.buffer.write(raw)
        elif config['profile'] == 'html-text-utf8/1':
            parser = Emitter(syntax, config['limits']['stdout_bytes'], config['limits']['syntax_bytes'])
            parser.feed(text)
            parser.close()
        else:
            raise ValueError('unsupported fixed profile')
    behavior = config['test_only_behavior']
    if behavior != 'normal' and config['purpose'] != 'TEST_ONLY':
        raise ValueError('TEST_ONLY behavior in actual plan')
    if behavior in ('diagnostic', 'nonzero'):
        sys.stderr.buffer.write(b'TEST_ONLY fixed diagnostic\n')
    if runtime_files() != before:
        raise ValueError('runtime-files-changed')
    sys.stdout.buffer.flush()
    sys.stderr.buffer.flush()
    return 7 if behavior == 'nonzero' else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, UnicodeError, OSError) as exc:
        sys.stderr.write(type(exc).__name__ + ': ' + str(exc) + '\n')
        raise SystemExit(8)
