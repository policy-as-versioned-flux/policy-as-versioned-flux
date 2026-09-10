"""The deck's public recorded-run reader follows a distinct observation ref."""
import importlib.util
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('observation_deck', ROOT / 'talk/build_deck.py')
deck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deck)


class ObservationRecords(unittest.TestCase):
    def test_recording_ref_preserves_historical_and_new_captures_without_changing_source(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / 'repo'
            repo.mkdir()
            no_hooks = Path(td) / 'hooks'
            no_hooks.mkdir()
            def git(*args):
                return subprocess.check_output(['git', '-c', f'core.hooksPath={no_hooks}', '-C', str(repo), *args], text=True).strip()
            def commit(message):
                git('add', '-Af', '.')
                git('-c', 'commit.gpgsign=false', 'commit', '-qm', message)
                return git('rev-parse', 'HEAD')
            git('init', '-q', '-b', 'main')
            git('config', 'user.name', 'fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (repo / 'source.txt').write_text('first source\n')
            source1 = commit('source one')
            captures = repo / 'talk/captures'
            captures.mkdir(parents=True)
            line1 = f'TRUTH 1970-01-01T00:00Z run=1 hub={source1} pass=1 fail=0 skip=0'
            (repo / 'talk/truth.log').write_text(line1 + '\n')
            (captures / 'proof.out').write_text('first observation\n')
            record1 = commit('truth: record run 1')
            git('branch', 'observations')
            (repo / 'source.txt').write_text('second source\n')
            source2 = commit('source two')
            git('checkout', '-q', 'observations')
            line2 = f'TRUTH 1970-01-02T00:00Z run=2 hub={source2} pass=0 fail=1 skip=0'
            (repo / 'talk/truth.log').write_text(line1 + '\n' + line2 + '\n')
            (captures / 'proof.out').write_text('second observation\n')
            record2 = commit('truth: record run 2')
            git('checkout', '-q', 'main')
            (captures / 'proof.out').write_text('local rehearsal, not evidence\n')
            self.assertEqual(deck.named_run('newest', repo, record_ref='observations'), (line2, record2))
            self.assertEqual(deck.named_run('1', repo, record_ref='observations'), (line1, record1))
            self.assertNotEqual(source2, record2)
            self.assertEqual(git('rev-parse', 'HEAD'), source2)
            exported = deck.export_captures(record2, repo / 'export', repo)
            self.assertEqual((exported / 'proof.out').read_text(), 'second observation\n')
            self.assertEqual(deck.named_run('newest', repo), (line1, record1))
            for filename in ('build_deck.py', 'truth_manifest.py', 'narration.json'):
                shutil.copyfile(ROOT / 'talk' / filename, repo / 'talk' / filename)
            built = deck.build('newest', repo, record_ref='observations')
            self.assertEqual(deck.deck_name(built)['hub'], source2)
            self.assertEqual(deck.deck_name(built)['recording'], record2)
            self.assertIn(line2, built)
            selected_default = deck.build(root=repo, record_ref='observations')
            self.assertEqual(deck.deck_name(selected_default)['recording'], record2)
            self.assertNotIn('local rehearsal, not evidence', built)
            marker = repo / 'deck.md'
            marker.write_text(f'<!-- deck run=2 hub={source2} source=recorded recording={record2} -->')
            cli = subprocess.run([sys.executable, str(repo / 'talk/build_deck.py'),
                                  '--record-ref', 'observations', '--name', str(marker)],
                                 capture_output=True, text=True)
            self.assertEqual(cli.returncode, 0, cli.stderr + cli.stdout)
            self.assertIn(f'hub={source2}', cli.stdout)
            self.assertIn(f'recording={record2}', cli.stdout)
            with self.assertRaises(deck.CouldNotLook):
                deck.named_run('newest', repo, record_ref='missing-observations')
            only_observations = repo / 'without-source'
            subprocess.run(['git', '-c', f'core.hooksPath={no_hooks}', 'clone', '-q', '--single-branch', '--branch=observations',
                            repo.as_uri(), str(only_observations)], check=True)
            with self.assertRaises(deck.CouldNotLook):
                deck.named_run('newest', only_observations, record_ref='HEAD')
            shallow = repo / 'shallow'
            subprocess.run(['git', '-c', f'core.hooksPath={no_hooks}', 'clone', '-q', '--depth=1', '--branch=observations',
                            repo.as_uri(), str(shallow)], check=True)
            with self.assertRaises(deck.CouldNotLook):
                deck.named_run('newest', shallow, record_ref='HEAD')


if __name__ == '__main__':
    unittest.main()


def test_rewritten_truth_line_cannot_borrow_original_recording_captures(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    no_hooks = tmp_path / 'hooks'
    no_hooks.mkdir()

    def git(*args):
        return subprocess.check_output(
            ['git', '-c', f'core.hooksPath={no_hooks}', '-c', 'commit.gpgsign=false',
             '-C', str(repo), *args], text=True).strip()

    git('init', '-q', '-b', 'main')
    git('config', 'user.name', 'fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    (repo / 'talk/captures').mkdir(parents=True)
    for filename in ('build_deck.py', 'truth_manifest.py', 'narration.json'):
        shutil.copyfile(ROOT / 'talk' / filename, repo / 'talk' / filename)
    git('add', '-A')
    git('commit', '-qm', 'source')
    source = git('rev-parse', 'HEAD')
    line = f'TRUTH 1970-01-01T00:00Z run=1 hub={source} pass=0 fail=1 skip=0'
    log = repo / 'talk/truth.log'
    log.write_text(line + '\n')
    (repo / 'talk/captures/proof.out').write_text('FAIL: the observation failed\n')
    git('add', '-A')
    git('commit', '-qm', 'truth: record run 1')
    original_recording = git('rev-parse', 'HEAD')
    original_deck = deck.build('1', repo, record_ref='HEAD')
    log.write_text(line.replace('pass=0 fail=1', 'pass=1 fail=0') + '\n')
    git('add', 'talk/truth.log')
    git('commit', '-qm', 'rewrite the earlier result without appending a run')

    # The selected line is now green, while the real append and its captures are red.
    # Returning either a tuple of mismatched evidence or an old line is not acceptable.
    import pytest
    with pytest.raises(deck.CouldNotLook):
        deck.named_run('newest', repo, record_ref='HEAD')
    with pytest.raises(deck.CouldNotLook):
        deck.build('1', repo, record_ref='HEAD')
    deck_path = repo / 'deck.md'
    deck_path.write_text(original_deck)
    with pytest.raises(deck.CouldNotLook):
        deck.check(deck_path, repo, record_ref='HEAD')
    cli = subprocess.run([sys.executable, str(repo / 'talk/build_deck.py'),
                          '--record-ref', 'HEAD', '--name', str(deck_path)],
                         capture_output=True, text=True)
    assert cli.returncode == 3, cli.stdout + cli.stderr
    assert 'could not look' in cli.stdout
    assert f'recording={original_recording}' not in cli.stdout
