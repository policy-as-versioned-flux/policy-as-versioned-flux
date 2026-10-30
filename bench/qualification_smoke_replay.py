"""Replay existing host-pinned smoke evidence; never load a model or qualify it."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from twin.development_capture import demonstrate

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('evidence', 'corpus', 'producer', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--manifest-pin', required=True)
    parser.add_argument('--at', default=None, help='host record timestamp; defaults to current UTC')
    args = parser.parse_args()
    recorded_at = args.at or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(json.dumps(demonstrate(args.evidence, args.manifest_pin, args.corpus, args.producer,
                                args.output, recorded_at), indent=2))
