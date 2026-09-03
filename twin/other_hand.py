"""The other hand: the second identity on the merge button.

Ticket 75 Q6 and Q14 (2026-09-02, the owner, reasoned): principle 5, "a human merges", binds for
the demonstration, and for the development window the assistant reviews and merges as a second
machine identity while the owner authors and pushes. The identity is the GitHub App
`pavc-other-hand` (App ID 4819564, owned by the policy-as-versioned-flux org, installable on any
account so it reaches all nine estate orgs). Ticket 88 records its creation.

What this module does: mint the two credentials a GitHub App needs, from a private key that
lives outside every repository.

1. `app_jwt` -- a nine-minute RS256 JWT that says "I am the app". Signed with `openssl` so the
   repository takes no new dependency; the key is a *path*, read at call time, never held.
2. `installation_token` -- a one-hour token for one installation (one org), minted with that JWT.
   This is what `gh` and `git` use, via `GH_TOKEN`.

What it deliberately does not do: store a token, cache a key, or read a credential from anywhere
but the path in `PAVC_OTHER_HAND_KEY` (default `~/.config/pavc-other-hand/app.pem`). A commit made
with an installation token is attributed to `pavc-other-hand[bot]`, which is the point: every
merge shows a second identity, and that identity's signature attests the absence of a human
(NORTH-STAR principle 6).

CLI:

    python -m twin.other_hand whoami                 # the app's slug, proves the key works
    python -m twin.other_hand installations          # org -> installation id
    python -m twin.other_hand token --org <org>      # prints an installation token for that org

    GH_TOKEN="$(python -m twin.other_hand token --org policy-as-versioned-driftwood)" gh api ...
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

API = "https://api.github.com"
APP_ID = "4819564"
APP_SLUG = "pavc-other-hand"
DEFAULT_KEY_PATH = Path.home() / ".config" / "pavc-other-hand" / "app.pem"

Opener = Callable[[str, str, str, "dict[str, Any] | None"], Any]


class OtherHandError(RuntimeError):
    """A credential could not be minted. The message says which step and why."""


@dataclass(frozen=True)
class Settings:
    app_id: str
    key_path: Path


def settings() -> Settings:
    """Environment first, then the registered defaults. Nothing here is a secret: the app id
    is public metadata and the key path is a location, not a key."""
    return Settings(
        app_id=os.environ.get("PAVC_OTHER_HAND_APP_ID", APP_ID),
        key_path=Path(os.environ.get("PAVC_OTHER_HAND_KEY", str(DEFAULT_KEY_PATH))).expanduser(),
    )


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def app_jwt(app_id: str, key_path: Path, now: int | None = None) -> str:
    """A nine-minute RS256 JWT with the app as issuer. `iat` is backdated sixty seconds because
    GitHub rejects a token whose `iat` is ahead of its own clock; `exp` stays under the
    ten-minute cap."""
    if not key_path.is_file():
        raise OtherHandError(f"private key not found at {key_path}; see ticket 88 for where it lives")
    at = int(time.time()) if now is None else now
    header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64url(
        json.dumps({"iat": at - 60, "exp": at + 540, "iss": app_id}, separators=(",", ":")).encode()
    )
    signing_input = f"{header}.{payload}".encode("ascii")
    result = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(key_path)],
        input=signing_input, capture_output=True,
    )
    if result.returncode != 0:
        raise OtherHandError(f"openssl could not sign with {key_path}: {result.stderr.decode(errors='replace').strip()}")
    return f"{header}.{payload}.{_b64url(result.stdout)}"


def _http(method: str, path: str, bearer: str, body: dict[str, Any] | None = None) -> Any:
    """One JSON call to the GitHub API with a bearer credential. Kept tiny so tests can swap it."""
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        API + path, data=data, method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {bearer}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": APP_SLUG,
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - fixed https host
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise OtherHandError(f"{method} {path} -> HTTP {exc.code}: {detail}") from exc


def whoami(jwt: str, opener: Opener = _http) -> str:
    """The app's slug, read with the JWT. If this returns, the key and the app id agree."""
    return str(opener("GET", "/app", jwt, None)["slug"])


def installations(jwt: str, opener: Opener = _http) -> dict[str, int]:
    """Account login -> installation id, for every account the app is installed on."""
    rows = opener("GET", "/app/installations", jwt, None)
    return {str(row["account"]["login"]): int(row["id"]) for row in rows}


def installation_for_org(jwt: str, org: str, opener: Opener = _http) -> int:
    found = installations(jwt, opener=opener)
    if org not in found:
        raise OtherHandError(f"{APP_SLUG} is not installed on {org}; installed on: {sorted(found) or 'nothing'}")
    return found[org]


def installation_token(jwt: str, installation_id: int, opener: Opener = _http) -> str:
    """A one-hour token scoped to one installation. Printed, never stored."""
    return str(opener("POST", f"/app/installations/{installation_id}/access_tokens", jwt, {})["token"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="twin.other_hand", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("whoami", help="print the app slug the key authenticates as")
    sub.add_parser("installations", help="print org -> installation id")
    token = sub.add_parser("token", help="print an installation token for one org")
    token.add_argument("--org", required=True)
    args = parser.parse_args(argv)

    cfg = settings()
    try:
        jwt = app_jwt(cfg.app_id, cfg.key_path)
        if args.command == "whoami":
            print(whoami(jwt))
        elif args.command == "installations":
            for login, installation_id in sorted(installations(jwt).items()):
                print(f"{login}\t{installation_id}")
        else:
            print(installation_token(jwt, installation_for_org(jwt, args.org)))
    except OtherHandError as exc:
        print(f"other-hand: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
