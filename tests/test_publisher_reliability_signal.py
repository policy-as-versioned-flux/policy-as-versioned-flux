"""The real report's publication is a signal, never a calibrated price or forecast.

The fixture is the unchanged report from NIST fd93b161, signed release
publisher-reliability/v1.0.0. This pure test performs no signature verification.
Run directly to exercise only the signal module, without the actor test harness.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from twin.feed_signal import FeedSignalError, signal_for, steep_for


class PublisherReliabilitySignalTests(unittest.TestCase):
    def test_actual_unmeasured_report_becomes_only_a_publication_signal(self) -> None:
        fixture = Path(__file__).parent / 'fixtures/publisher-reliability-v1.0.0.json'
        raw = fixture.read_bytes()
        envelope = json.loads(raw)
        original = copy.deepcopy(envelope)
        payload = envelope['payload']
        self.assertEqual(payload['status'], 'unmeasured')
        self.assertEqual(payload['counts']['eligible'], 0)
        self.assertIsNone(payload['losses']['brier'])
        self.assertIsNone(payload['losses']['log_loss'])
        tag = 'publisher-reliability/v1.0.0'
        commit = 'fd93b1612a3495c45bde9191ff2b67478ad46877'
        signal = signal_for(envelope, tag=tag, commit=commit)
        self.assertEqual(steep_for(envelope['name']), 'technological')
        self.assertEqual(signal['id'], 'nist-publisher-reliability-1-0-0-published')
        self.assertEqual(signal['date'], envelope['published_at'][:10])
        self.assertEqual(signal['steep'], 'technological')
        self.assertEqual(signal['source'], tag)
        self.assertEqual(signal['statement'],
                         'nist published publisher-reliability version 1.0.0 on '
                         f"{envelope['published_at']}, and this organisation pins it.")
        provenance = signal['provenance']
        self.assertEqual(provenance['commit'], commit)
        self.assertEqual(provenance['tag'], tag)
        self.assertEqual(provenance['published_at'], envelope['published_at'])
        self.assertEqual(provenance['date_basis'], 'envelope.published_at')
        self.assertEqual(provenance['evidence_grade'], 5)
        self.assertIn('grade 5', provenance['contestable'])
        self.assertIn('never prices', provenance['contestable'])
        self.assertEqual(set(signal), {'id', 'date', 'steep', 'source', 'statement', 'provenance'})
        self.assertEqual(set(provenance), {
            'published_at', 'tag', 'commit', 'feed', 'version', 'published_by',
            'bound_by', 'evidence_grade', 'contestable', 'date_basis',
        })
        self.assertEqual(envelope, original)
        self.assertEqual(fixture.read_bytes(), raw)

    def test_unknown_feed_and_reasoned_news_exclusion_still_refuse(self) -> None:
        for name, reason in [('weather', 'no row in STEEP_BY_FEED'), ('news', 'excluded')]:
            with self.subTest(name=name):
                with self.assertRaisesRegex(FeedSignalError, reason):
                    steep_for(name)


if __name__ == '__main__':
    unittest.main()
