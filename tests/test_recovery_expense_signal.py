"""A genuine prospective expense model publishes a signal, never an observed loss.

The fixture is byte-identical to feeds 838abe58's signed recovery-expense/v1.0.2
envelope. These pure caller tests perform no signature verification or pricing.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from twin.feed_signal import FeedSignalError, signal_for


FIXTURE = Path(__file__).parent / 'fixtures/recovery-expense-v1.0.2.json'
TAG = 'recovery-expense/v1.0.2'
COMMIT = '838abe583f14f07c82ef1eccfcf9ca3acfdf80fa'


class RecoveryExpenseSignalTests(unittest.TestCase):
    def test_actual_prospective_model_becomes_only_a_publication_signal(self) -> None:
        raw = FIXTURE.read_bytes()
        envelope = json.loads(raw)
        original = copy.deepcopy(envelope)
        self.assertEqual(envelope['name'], 'recovery-expense')
        self.assertEqual(envelope['payload']['currency'], 'GBP')

        signal = signal_for(envelope, tag=TAG, commit=COMMIT)

        self.assertEqual(signal['id'], 'feeds-recovery-expense-1-0-2-published')
        self.assertEqual(signal['steep'], 'economic')
        self.assertEqual(signal['date'], envelope['published_at'][:10])
        self.assertEqual(signal['source'], TAG)
        self.assertEqual(signal['statement'],
                         'feeds published recovery-expense version 1.0.2 on '
                         f"{envelope['published_at']}, and this organisation pins it.")
        provenance = signal['provenance']
        self.assertEqual(provenance['tag'], TAG)
        self.assertEqual(provenance['commit'], COMMIT)
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
        self.assertEqual(signal_for(envelope, tag=TAG, commit=COMMIT), signal)
        self.assertEqual(envelope, original)
        self.assertEqual(FIXTURE.read_bytes(), raw)

    def test_real_model_still_needs_provenance_and_refuses_injection(self) -> None:
        envelope = json.loads(FIXTURE.read_bytes())
        for tag, commit in [('', COMMIT), (TAG, '')]:
            with self.subTest(tag=tag, commit=commit):
                with self.assertRaisesRegex(FeedSignalError, 'signed tag'):
                    signal_for(envelope, tag=tag, commit=commit)
        with self.assertRaisesRegex(FeedSignalError, 'injected'):
            signal_for({**envelope, 'injected': True}, tag=TAG, commit=COMMIT)


if __name__ == '__main__':
    unittest.main()
