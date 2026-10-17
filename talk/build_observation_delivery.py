#!/usr/bin/env python3
"""Build the immutable reviewer from one implementation and its three trusted helpers.

ZIP_STORED, fixed timestamps/modes and sorted members make identical source bytes
produce identical bundles across Python versions. No dependency or network lookup
participates in this build. Callers pin both the publishing commit and bundle hash.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'observation_delivery.py': 'talk/observation_delivery.py',
    'delivery_truth_integration.py': 'talk/truth_integration.py',
    'delivery_enact_record.py': 'verify/enact-record/enact_record.py',
    'delivery_other_hand.py': 'twin/other_hand.py',
}


def build(root: Path = ROOT) -> bytes:
    files = {name: (root / path).read_bytes() for name, path in SOURCES.items()}
    manifest = {name: {'source': SOURCES[name], 'sha256': hashlib.sha256(data).hexdigest()}
                for name, data in files.items()}
    files['SOURCE.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    files['__main__.py'] = b'from observation_delivery import main\nraise SystemExit(main())\n'
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'talk/observation-delivery.pyz')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = build()
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != data:
            raise SystemExit('immutable observation bundle is stale; rebuild from reviewed sources')
    else:
        args.output.write_bytes(data)
    print(hashlib.sha256(data).hexdigest() + '  ' + args.output.name)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
