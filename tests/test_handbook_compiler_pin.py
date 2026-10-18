"""The public handbook CLI reads compiler declarations at the ref being graded.

The Git stores and renderer programs are explicit fixtures, not authenticated releases.
Expected served pages are literals independent of the renderer under test.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


GRADER = Path(__file__).resolve().parents[1] / "verify/handbook/handbook_check.py"
TOOLS_PIN = ".github/platform-tools-pin.yaml"
POLICY_PIN = "gitops/platform/platform-pin.yaml"
PLATFORM_URL = "https://github.com/policy-as-versioned-platform/platform"
OLD_PAGE = "# Fixture handbook\nAmount: 7\n"
COMPILER_PAGE = "# Fixture handbook\nAmount: 7\nNew metadata: counted\n"


class HandbookCompilerPinCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.estate = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("GIT_", "PAVC_")) and k not in {"PYTHONPATH", "PYTHONHOME"}}
        self.env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null",
                        GIT_TERMINAL_PROMPT="0", PYTHONDONTWRITEBYTECODE="1")
        self.platform = self.repo("platform")
        self.git(self.platform, "remote", "add", "origin", PLATFORM_URL + ".git")
        self.write(self.platform, "compose/handbook.py", self.renderer(False))
        self.policy_commit = self.commit(self.platform, "policy renderer")
        self.git(self.platform, "tag", "v1.0.0")
        self.write(self.platform, "compose/handbook.py", self.renderer(True))
        self.compiler_commit = self.commit(self.platform, "compiler renderer")
        self.git(self.platform, "tag", "-a", "v2.0.0", "-m", "structural compiler fixture, not authenticated")
        self.adopter = self.repo("driftwood")
        self.write(self.adopter, POLICY_PIN, self.pin("v1.0.0", self.policy_commit))
        self.write(self.adopter, "composed/evidence.json",
                   json.dumps({"prices": [{"amount": 7}], "note": "counted"}))
        self.write(self.adopter, "composed/HANDBOOK.md", COMPILER_PAGE)

    def git(self, repo: Path, *args: str) -> str:
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       env=self.env, stderr=subprocess.PIPE, text=True).strip()

    def repo(self, name: str) -> Path:
        repo = self.estate / name
        repo.mkdir()
        self.git(repo, "init", "-q", "-b", "main")
        for key, value in (("user.name", "Handbook fixture"), ("user.email", "fixture@example.invalid"),
                           ("commit.gpgsign", "false"), ("tag.gpgsign", "false")):
            self.git(repo, "config", key, value)
        return repo

    def write(self, repo: Path, path: str, text: str) -> None:
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, repo: Path, message: str) -> str:
        self.git(repo, "add", "--all")
        self.git(repo, "commit", "-q", "-m", message)
        self.git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        return self.git(repo, "rev-parse", "HEAD")

    def pin(self, tag: str, commit: str) -> str:
        return ("apiVersion: source.toolkit.fluxcd.io/v1\nkind: GitRepository\n"
                "metadata: {name: platform-tools}\nspec:\n"
                f"  url: {PLATFORM_URL}\n  ref: {{tag: {tag}, commit: {commit}}}\n")

    def renderer(self, modern: bool) -> str:
        extra = "    page += 'New metadata: ' + evidence['note'] + '\\n'\n" if modern else ""
        return ("def render(files, evidence):\n"
                "    page = '# Fixture handbook\\nAmount: ' + str(evidence['prices'][0]['amount']) + '\\n'\n"
                + extra + "    return page\n\n"
                "if __name__ == '__main__':\n"
                "    import json, sys\n    from pathlib import Path\n"
                "    root = Path(sys.argv[2])\n"
                "    print(render({}, json.loads((root / 'composed/evidence.json').read_text())), end='')\n")

    def cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(GRADER), str(self.estate)],
                              env=self.env, capture_output=True, text=True)

    def test_declared_compiler_renders_the_served_page_independently_of_accepted_policy(self) -> None:
        self.write(self.adopter, TOOLS_PIN, self.pin("v2.0.0", self.compiler_commit))
        self.commit(self.adopter, "independent compiler declaration")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("v2.0.0", result.stdout)
        self.assertIn("byte-identical", result.stdout)

    def test_present_malformed_compiler_is_named_false_without_policy_fallback(self) -> None:
        self.write(self.adopter, "composed/HANDBOOK.md", OLD_PAGE)
        self.write(self.adopter, TOOLS_PIN, "not a compiler declaration\n")
        self.commit(self.adopter, "malformed explicit compiler")
        result = self.cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("invalid compiler declaration", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_declared_tag_must_resolve_to_its_declared_commit(self) -> None:
        self.write(self.adopter, TOOLS_PIN, self.pin("v2.0.0", self.policy_commit))
        self.commit(self.adopter, "mismatched compiler pair")
        result = self.cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("tag/commit mismatch", result.stdout)

    def test_an_unavailable_explicit_compiler_does_not_borrow_a_working_policy_renderer(self) -> None:
        self.write(self.adopter, "composed/HANDBOOK.md", OLD_PAGE)
        self.write(self.adopter, TOOLS_PIN, self.pin("v9.0.0", self.compiler_commit))
        self.commit(self.adopter, "unavailable compiler")
        result = self.cli()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("v9.0.0", result.stdout)
        self.assertNotIn("byte-identical", result.stdout)

    def test_compiler_declaration_and_checkout_must_name_the_platform_publisher(self) -> None:
        self.write(self.adopter, TOOLS_PIN, self.pin("v2.0.0", self.compiler_commit).replace(
            PLATFORM_URL, "https://github.com/other/publisher"))
        self.commit(self.adopter, "wrong compiler publisher declaration")
        result = self.cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("compiler publisher", result.stdout)
        self.write(self.adopter, TOOLS_PIN, self.pin("v2.0.0", self.compiler_commit))
        self.commit(self.adopter, "correct declaration but wrong checkout")
        self.git(self.platform, "remote", "set-url", "origin", "https://github.com/other/publisher.git")
        result = self.cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("compiler publisher", result.stdout)

    def test_present_compiler_fields_are_typed_and_never_fall_back(self) -> None:
        for bad in ("kind: GitRepository\n", "spec: {ref: []}\n",
                    self.pin("v2.0.0", self.compiler_commit).replace("tag: v2.0.0", "tag: true"),
                    self.pin("v2.0.0", self.compiler_commit).replace(self.compiler_commit, "true"),
                    self.pin("v2.0.0", self.compiler_commit).replace("kind: GitRepository", "kind: ConfigMap"),
                    self.pin("v2.0.0", self.compiler_commit).replace(PLATFORM_URL, "[]"),
                    "spec: [unterminated\n"):
            with self.subTest(declaration=bad):
                self.write(self.adopter, TOOLS_PIN, bad)
                self.commit(self.adopter, "invalid compiler declaration")
                result = self.cli()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("invalid compiler declaration", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_each_graded_ref_uses_its_own_compiler_and_the_signed_tag_is_still_graded(self) -> None:
        self.write(self.adopter, "composed/HANDBOOK.md", OLD_PAGE)
        self.write(self.adopter, TOOLS_PIN, self.pin("v1.0.0", self.policy_commit))
        self.commit(self.adopter, "older compiler at the composed release")
        self.git(self.adopter, "tag", "-a", "composed-v1", "-m",
                 "Structural fixture only\n-----BEGIN TEST SIGNATURE-----\nnot authenticated")
        self.write(self.adopter, "composed/HANDBOOK.md", COMPILER_PAGE)
        self.write(self.adopter, TOOLS_PIN, self.pin("v2.0.0", self.compiler_commit))
        self.commit(self.adopter, "new compiler only on served branch")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("driftwood@origin/main", result.stdout)
        self.assertIn("driftwood@composed-v1", result.stdout)
        self.assertIn("declared at composed-v1 (v1.0.0@", result.stdout)
        self.assertIn("declared at origin/main (v2.0.0@", result.stdout)
        self.assertIn("1 of 1 also serve one at a signed tag", result.stdout)

    def test_absent_compiler_retains_the_historical_policy_renderer(self) -> None:
        self.write(self.adopter, "composed/HANDBOOK.md", OLD_PAGE)
        self.commit(self.adopter, "historical source without independent compiler")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("the platform tag this adopter pins (v1.0.0)", result.stdout)

    def test_unpublished_working_compiler_declaration_does_not_change_the_graded_ref(self) -> None:
        self.write(self.adopter, TOOLS_PIN, self.pin("v2.0.0", self.compiler_commit))
        self.commit(self.adopter, "published compiler")
        self.write(self.adopter, TOOLS_PIN, "not a declaration in the working tree\n")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_explicit_compiler_without_a_renderer_is_unavailable_not_a_policy_fallback(self) -> None:
        self.git(self.platform, "rm", "compose/handbook.py")
        no_renderer = self.commit(self.platform, "compiler missing its renderer")
        self.git(self.platform, "tag", "v3.0.0")
        self.write(self.adopter, "composed/HANDBOOK.md", OLD_PAGE)
        self.write(self.adopter, TOOLS_PIN, self.pin("v3.0.0", no_renderer))
        self.commit(self.adopter, "explicit compiler has no render instrument")
        result = self.cli()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("could not read the served artefact or renderer", result.stdout)

    def test_a_present_compiler_whose_blob_is_unreadable_is_not_treated_as_absent(self) -> None:
        self.write(self.adopter, "composed/HANDBOOK.md", OLD_PAGE)
        self.write(self.adopter, TOOLS_PIN, self.pin("v2.0.0", self.compiler_commit))
        self.commit(self.adopter, "present compiler declaration")
        blob = self.git(self.adopter, "rev-parse", "origin/main:" + TOOLS_PIN)
        # Damage this disposable real Git store, not a mocked reader or published input.
        (self.adopter / ".git/objects" / blob[:2] / blob[2:]).unlink()
        result = self.cli()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertNotIn("byte-identical", result.stdout)


if __name__ == "__main__":
    unittest.main()
