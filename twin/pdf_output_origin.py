"""Pure replay of the fixed Xpdf origin wire protocol.

A structural map establishes internal byte/origin consistency only. It is not an
execution receipt, native observation, publisher authentication or authority. This
module never launches a tool, reads a PDF, installs a handle or selects an index.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

PROFILE = 'pdf-text-xpdf-origin/2'
PROTOCOL_SHA256 = 'ce22a762c8e900c331a4d0c9ef87a402f5e7b8527050a20f04d55d1656bcb664'
SCHEMA_SHA256 = 'b945d708e188a272d93edf438f605fc06333e9b20e1894aaedb82c3f222b5491'
MAX_WIRE_BYTES = 64 * 1048576
MAX_RECORD_BYTES = 65536
MAX_EVENTS = 1000000
MAX_OUTPUT_BYTES = 128 * 1048576
MAX_CODE_BYTES = 256 * 1048576
MAX_SCALARS = 4096
HEADER = {'schema':'twin.pdf-output-origin-events/v1', 'profile':PROFILE,
          'emitter_protocol_version':1}
FIELDS = {
    'fragment_open': ('fragment','page','code_bytes','code_sha256'),
    'item': ('item','fragment','code_start','code_end','code_hex','input_scalars','scalars','taint'),
    'fragment_close': ('fragment','consumed_code_bytes'),
    'emit': ('start','end','operation','origin_item','origin_scalar','reason','utf8_hex'),
    'barrier': ('at','reason'),
    'omit': ('item','scalar','reason'),
}
FOOTER_FIELDS = ('record','closed_fragment_count','emitted_stdout_bytes','emitted_stdout_sha256',
                 'event_count','event_prefix_bytes','event_prefix_sha256','intended_exit_code')


class PdfOriginHold(ValueError):
    """Structural inconsistency or an unsupported witness, never successful authority."""


@dataclass(frozen=True, init=False, repr=False, eq=False)
class PdfOriginMap:
    """Passive verifier result; public serialized descriptions cannot adopt this type."""
    description: bytes
    _runs: tuple[tuple[int, int, bool, int], ...]
    _barriers: frozenset[int]
    _boundaries: frozenset[int]
    _output_bytes: int
    _output: bytes
    _content_sha256: str


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _closed(value: Any, fields: set[str]) -> None:
    if type(value) is not dict or set(value) != fields:
        raise PdfOriginHold('closed origin record required')


def _int(value: Any, maximum: int, minimum: int = 0) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise PdfOriginHold('bounded origin integer required')
    return value


def _hash(value: Any) -> str:
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise PdfOriginHold('origin hash required')
    return value


def _hex(value: Any, maximum: int) -> bytes:
    if (type(value) is not str or len(value) % 2 or len(value) > 2 * maximum
            or any(c not in '0123456789abcdef' for c in value)):
        raise PdfOriginHold('bounded lowercase origin hex required')
    return bytes.fromhex(value)


def _scalars(value: Any) -> list[int]:
    if type(value) is not list or len(value) > MAX_SCALARS:
        raise PdfOriginHold('bounded origin scalar array required')
    for scalar in value:
        _int(scalar, 0x10ffff)
        if 0xd800 <= scalar <= 0xdfff:
            raise PdfOriginHold('surrogate is not a Unicode scalar')
    return value


def _record(raw: bytes) -> dict:
    if not raw.endswith(b'\n') or len(raw) > MAX_RECORD_BYTES or raw == b'\n':
        raise PdfOriginHold('bounded LF-terminated origin record required')
    try:
        value = json.loads(raw)
        # Equality to canonical serialization also rejects duplicate keys, whitespace,
        # alternate number/escape forms, non-ASCII strings and embedded/trailing lines.
        if type(value) is not dict or _canonical(value) + b'\n' != raw:
            raise PdfOriginHold('canonical origin JSON required')
    except (ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        raise PdfOriginHold('invalid canonical origin JSON') from exc
    return value


def _discontinuities(previous: tuple[int, int] | None, current: tuple[int, int],
                     items: dict[int, dict], repeated: bool) -> set[str]:
    if previous is None:
        return set()
    old_id, old_scalar = previous
    item_id, scalar = current
    old, item = items[old_id], items[item_id]
    reasons = set()
    if repeated:
        reasons.add('duplicate')
    if old_id == item_id:
        if scalar != old_scalar + 1:
            reasons.add('scalar-order')
    elif old['fragment'] != item['fragment'] or item['fragment'] == 0:
        reasons.add('fragment')
    else:
        if old_scalar != len(old['scalars']) - 1 or scalar != 0 or item_id < old_id:
            reasons.add('scalar-order')
        if old['code_end'] != item['code_start']:
            reasons.add('source-gap')
    return reasons


def check_pdf_origin_events(output: bytes, raw_events: bytes) -> PdfOriginMap:
    """Rebuild the fixed protocol's structural map; acquire no actual/native state."""
    if type(output) is not bytes or type(raw_events) is not bytes:
        raise PdfOriginHold('exact captured bytes required')
    if len(output) > MAX_OUTPUT_BYTES or len(raw_events) > MAX_WIRE_BYTES:
        raise PdfOriginHold('origin stream limit')
    try:
        output.decode('utf8', errors='strict')
    except UnicodeError as exc:
        raise PdfOriginHold('output must be complete UTF-8') from exc
    # Work is bounded by the complete wire cap. Iterating LF offsets avoids another
    # full list/copy of a maximum-size stream and hashes the exact received prefix.
    offset = 0
    prefix = hashlib.sha256()
    prefix_bytes = 0
    event_count = 0
    footer = None
    active = None
    fragments: dict[int, dict] = {}
    items: dict[int, dict] = {}
    accounted: set[tuple[int, int]] = set()
    emitted: set[tuple[int, int]] = set()
    last_fragment = last_item = closed_count = code_total = cursor = chain = 0
    previous = None
    previous_eligible = False
    barriers: set[int] = set()
    pending_barriers: set[str] = set()
    boundaries = {0}
    runs: list[tuple[int, int, bool, int]] = []
    while offset < len(raw_events):
        end_line = raw_events.find(b'\n', offset, min(len(raw_events), offset + MAX_RECORD_BYTES) + 1)
        if end_line < 0:
            raise PdfOriginHold('origin record missing LF or over limit')
        line = raw_events[offset:end_line+1]
        record = _record(line)
        offset = end_line + 1
        if prefix_bytes == 0:
            _closed(record, set(HEADER))
            if record != HEADER or type(record['emitter_protocol_version']) is not int:
                raise PdfOriginHold('fixed origin header required')
            prefix.update(line); prefix_bytes += len(line)
            continue
        if record.get('record') == 'footer':
            _closed(record, set(FOOTER_FIELDS))
            if offset != len(raw_events):
                raise PdfOriginHold('records after origin footer')
            footer = record
            break
        kind = record.get('record')
        if type(kind) is not str or kind not in FIELDS:
            raise PdfOriginHold('unknown origin event')
        _closed(record, set(FIELDS[kind]) | {'seq','record'})
        if _int(record['seq'], MAX_EVENTS) != event_count or event_count >= MAX_EVENTS:
            raise PdfOriginHold('origin event sequence/count differs')
        event_count += 1
        prefix.update(line); prefix_bytes += len(line)
        if kind == 'fragment_open':
            fragment = _int(record['fragment'], MAX_EVENTS, 1)
            if active is not None or fragment <= last_fragment:
                raise PdfOriginHold('nested/reused/out-of-order fragment')
            _int(record['page'], MAX_EVENTS, 1)
            size = _int(record['code_bytes'], MAX_CODE_BYTES)
            code_total += size
            if code_total > MAX_CODE_BYTES:
                raise PdfOriginHold('source code byte limit')
            active = fragment; last_fragment = fragment
            fragments[fragment] = {'bytes':size, 'hash':_hash(record['code_sha256']),
                                   'cursor':0, 'digest':hashlib.sha256(), 'closed':False}
        elif kind == 'item':
            item_id = _int(record['item'], MAX_EVENTS, 1)
            fragment = _int(record['fragment'], MAX_EVENTS)
            if item_id <= last_item:
                raise PdfOriginHold('reused/out-of-order decoder item')
            last_item = item_id
            code = _hex(record['code_hex'], 64)
            start = _int(record['code_start'], MAX_CODE_BYTES)
            end = _int(record['code_end'], MAX_CODE_BYTES)
            _scalars(record['input_scalars']); _scalars(record['scalars'])
            taint = record['taint']
            if taint not in ('none','unicode-remap','actualtext','unmapped'):
                raise PdfOriginHold('unknown origin taint')
            if taint == 'none' and record['input_scalars'] != record['scalars']:
                raise PdfOriginHold('unreported Unicode remapping')
            if fragment == 0:
                if code or start or end or taint != 'actualtext':
                    raise PdfOriginHold('replacement-only origin differs')
            else:
                if fragment != active or not code or end-start != len(code):
                    raise PdfOriginHold('decoder source code interval differs')
                state = fragments[fragment]
                if start != state['cursor'] or end > state['bytes']:
                    raise PdfOriginHold('decoder code coverage differs')
                state['cursor'] = end; state['digest'].update(code)
            items[item_id] = record
        elif kind == 'fragment_close':
            fragment = _int(record['fragment'], MAX_EVENTS, 1)
            consumed = _int(record['consumed_code_bytes'], MAX_CODE_BYTES)
            if fragment != active:
                raise PdfOriginHold('unknown/unmatched fragment close')
            state = fragments[fragment]
            if consumed != state['bytes'] or state['cursor'] != consumed or state['digest'].hexdigest() != state['hash']:
                raise PdfOriginHold('fragment code bytes/hash differ')
            state['closed'] = True; active = None; closed_count += 1
        elif kind == 'barrier':
            if _int(record['at'], len(output)) != cursor or record['reason'] not in ('fragment','source-gap','scalar-order','duplicate'):
                raise PdfOriginHold('origin join barrier differs')
            pending_barriers.add(record['reason']); barriers.add(cursor)
        elif kind == 'omit':
            key = (_int(record['item'], MAX_EVENTS, 1), _int(record['scalar'], MAX_SCALARS-1))
            if record['reason'] != 'not-emitted-by-reading-order' or key[0] not in items or key[1] >= len(items[key[0]]['scalars']) or key in accounted:
                raise PdfOriginHold('missing/repeated/emitted omission')
            accounted.add(key)
        elif kind == 'emit':
            start = _int(record['start'], len(output)); end = _int(record['end'], len(output))
            raw = _hex(record['utf8_hex'], MAX_RECORD_BYTES)
            if start != cursor or end <= start or end-start != len(raw) or output[start:end] != raw:
                raise PdfOriginHold('complete origin output partition differs')
            try:
                text = raw.decode('utf8', errors='strict')
            except UnicodeError as exc:
                raise PdfOriginHold('emit must follow UTF-8 scalar boundaries') from exc
            for char in text:
                boundaries.add(start); start += len(char.encode('utf8'))
            boundaries.add(end)
            item_id = _int(record['origin_item'], MAX_EVENTS)
            scalar = _int(record['origin_scalar'], MAX_SCALARS-1)
            operation, reason = record['operation'], record['reason']
            eligible = False
            if operation == 'generated':
                if item_id or scalar or reason not in ('spacing','linebreak','bidi','bom','pagebreak','unmapped'):
                    raise PdfOriginHold('typed generated output required')
                previous = None
            else:
                if item_id not in items or scalar >= len(items[item_id]['scalars']) or len(text) != 1:
                    raise PdfOriginHold('emit must reference one earlier decoder scalar')
                item = items[item_id]; key = (item_id, scalar); repeated = key in emitted
                if key in accounted and not repeated:
                    raise PdfOriginHold('omitted scalar emitted later')
                expected = chr(item['scalars'][scalar]).encode('utf8')
                if repeated:
                    if operation != 'modified' or reason != 'duplicate':
                        raise PdfOriginHold('reused scalar requires modified duplicate')
                elif operation == 'decoded':
                    if reason != 'source' or item['taint'] != 'none' or raw != expected:
                        raise PdfOriginHold('unchanged decoder output differs')
                    eligible = item['fragment'] != 0
                elif operation == 'modified':
                    taint_reason = {'unicode-remap':'remap','actualtext':'actualtext','unmapped':'unmapped'}
                    if reason != 'mirror' and (reason != taint_reason.get(item['taint']) or raw != expected):
                        raise PdfOriginHold('typed modification differs from decoder item')
                else:
                    raise PdfOriginHold('unknown output operation')
                required = _discontinuities(previous, key, items, repeated)
                if required and not required.intersection(pending_barriers):
                    raise PdfOriginHold('required independently reconstructed barrier missing')
                if not eligible or not previous_eligible or required or pending_barriers:
                    chain += 1
                previous = key; emitted.add(key); accounted.add(key)
            if not eligible:
                chain += 1
            runs.append((cursor, end, eligible, chain))
            cursor = end; previous_eligible = eligible; pending_barriers.clear()
    if footer is None or active is not None or pending_barriers or cursor != len(output):
        raise PdfOriginHold('origin stream/footer/fragment/output incomplete')
    for item_id, item in items.items():
        if any((item_id, scalar) not in accounted for scalar in range(len(item['scalars']))):
            raise PdfOriginHold('decoder scalar has neither emission nor omission')
    expected_footer = {'record':'footer', 'closed_fragment_count':closed_count,
        'emitted_stdout_bytes':len(output), 'emitted_stdout_sha256':_sha(output),
        'event_count':event_count, 'event_prefix_bytes':prefix_bytes,
        'event_prefix_sha256':prefix.hexdigest(), 'intended_exit_code':0}
    for field in ('closed_fragment_count','emitted_stdout_bytes','event_count','event_prefix_bytes','intended_exit_code'):
        _int(footer[field], MAX_CODE_BYTES)
    if footer != expected_footer:
        raise PdfOriginHold('origin footer hash/count/intention differs')
    description = {'schema':'twin.pdf-output-origin-map/v1', 'profile':PROFILE,
        'scope':'structural-only-no-native-authority', 'protocol_sha256':PROTOCOL_SHA256,
        'event_schema_sha256':SCHEMA_SHA256, 'output_sha256':_sha(output),
        'output_bytes':len(output), 'raw_events_sha256':_sha(raw_events),
        'raw_events_bytes':len(raw_events), 'runs':[list(run) for run in runs],
        'barriers':sorted(barriers), 'utf8_boundaries':sorted(boundaries)}
    description_raw = _canonical(description)
    result = object.__new__(PdfOriginMap)
    for name, value in [('description',description_raw), ('_runs',tuple(runs)),
            ('_barriers',frozenset(barriers)), ('_boundaries',frozenset(boundaries)),
            ('_output_bytes',len(output)), ('_output',output),
            ('_content_sha256',_sha(description_raw))]:
        object.__setattr__(result, name, value)
    return result


def _verified_map(origin_map: PdfOriginMap) -> None:
    """Check private passive content identity, without any public adoption path."""
    if type(origin_map) is not PdfOriginMap:
        raise PdfOriginHold('private structural verifier result required')
    try:
        description = json.loads(origin_map.description)
        expected = {'schema':'twin.pdf-output-origin-map/v1', 'profile':PROFILE,
            'scope':'structural-only-no-native-authority', 'protocol_sha256':PROTOCOL_SHA256,
            'event_schema_sha256':SCHEMA_SHA256, 'output_sha256':_sha(origin_map._output),
            'output_bytes':len(origin_map._output),
            'raw_events_sha256':_hash(description['raw_events_sha256']),
            'raw_events_bytes':_int(description['raw_events_bytes'],MAX_WIRE_BYTES),
            'runs':[list(run) for run in origin_map._runs],
            'barriers':sorted(origin_map._barriers),
            'utf8_boundaries':sorted(origin_map._boundaries)}
        if (type(origin_map.description) is not bytes
                or origin_map._output_bytes != len(origin_map._output)
                or _canonical(expected) != origin_map.description
                or _sha(origin_map.description) != origin_map._content_sha256):
            raise PdfOriginHold('private structural map content changed')
    except (AttributeError, KeyError, TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise PdfOriginHold('private structural map content required') from exc


def check_pdf_witness(origin_map: PdfOriginMap, start: int, end: int) -> None:
    """Check one structural witness; never establish run/custody/publisher authority."""
    _verified_map(origin_map)
    _int(start, origin_map._output_bytes); _int(end, origin_map._output_bytes)
    if end <= start or start not in origin_map._boundaries or end not in origin_map._boundaries:
        raise PdfOriginHold('nonempty UTF-8 scalar-aligned witness required')
    if any(start < boundary < end for boundary in origin_map._barriers):
        raise PdfOriginHold('publisher witness crosses origin join barrier')
    chains = set()
    for left, right, eligible, chain in origin_map._runs:
        if start < right and end > left:
            if not eligible:
                raise PdfOriginHold('publisher witness intersects generated/modified origin')
            chains.add(chain)
    if len(chains) != 1:
        raise PdfOriginHold('publisher witness requires one eligible continuity chain')


def check_pdf_publisher_witnesses(origin_map: PdfOriginMap, manifest: dict,
                                  member_id: str) -> None:
    """Structural gate for every publisher witness on one independently selected member.

    This does not validate the metadata schema, select a transform or admit a map to
    the migration authority. The caller must still enforce stock/custody checks. A
    derived alias of this member needs its own truthful verified provenance chain.
    """
    _verified_map(origin_map)
    if (type(manifest) is not dict or type(member_id) is not str
            or type(manifest.get('members')) is not dict
            or type(manifest.get('observations')) is not dict
            or type(manifest.get('statement')) is not dict
            or type(manifest.get('visible_excerpts')) is not list):
        raise PdfOriginHold('publisher manifest containers required')
    try:
        member = manifest['members'][member_id]
        if member['id'] != member_id or member['sha256'] != _sha(origin_map._output) or type(member['bytes']) is not int or member['bytes'] != len(origin_map._output):
            raise PdfOriginHold('selected member/output binding differs')
        witnesses = [row['witness'] for row in manifest['observations'].values()]
        if manifest['statement']['origin_role'] == 'publisher-quotation':
            witnesses.append(manifest['statement']['witness'])
        witnesses += [row['witness'] for row in manifest['visible_excerpts']
                      if row['origin_role'] == 'publisher-quotation']
        for witness in witnesses:
            selected = witness['member_id']
            seen = set()
            ancestor = selected
            while ancestor != member_id:
                if ancestor in seen:
                    raise PdfOriginHold('cyclic member provenance')
                seen.add(ancestor)
                parent = manifest['members'][ancestor].get('parent')
                if parent is None:
                    break
                ancestor = parent['member_id']
            if selected != member_id:
                if ancestor == member_id:
                    raise PdfOriginHold('derived alias requires independent verified provenance')
                continue
            _closed(witness, {'member_id','member_sha256','start_byte','end_byte','text_utf8'})
            if witness['member_sha256'] != member['sha256'] or type(witness['text_utf8']) is not str:
                raise PdfOriginHold('publisher witness member/text binding differs')
            check_pdf_witness(origin_map, witness['start_byte'], witness['end_byte'])
            if witness['text_utf8'].encode('utf8') != origin_map._output[witness['start_byte']:witness['end_byte']]:
                raise PdfOriginHold('publisher witness text differs')
    except (KeyError, TypeError, AttributeError, UnicodeError) as exc:
        raise PdfOriginHold('publisher witness structure differs') from exc
