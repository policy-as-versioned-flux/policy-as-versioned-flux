"""Content-hash references for bulk substrate.

Git-versioned text is the source of truth; the high-volume synthetic substrate (millions of
emails, chats, commits, telemetry) is the sole exception and is addressed by content hash rather
than held inline (decision ticket 07, Q4). Nothing produces substrate yet — the reference *form*
exists now because every later ticket writes into it, and it must round-trip with no substrate
present.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .canon import sha256_hex

_REF = re.compile(r"^(?P<algo>sha256):(?P<digest>[0-9a-f]{64}):(?P<size>\d+)$")


class BlobRefError(ValueError):
    pass


@dataclass(frozen=True)
class BlobRef:
    """`sha256:<64 hex>:<size in bytes>` — the whole reference, resolvable or not."""

    algo: str
    digest: str
    size: int

    def __str__(self) -> str:
        return f"{self.algo}:{self.digest}:{self.size}"

    @classmethod
    def of(cls, data: bytes) -> "BlobRef":
        return cls(algo="sha256", digest=sha256_hex(data), size=len(data))

    @classmethod
    def parse(cls, text: str) -> "BlobRef":
        m = _REF.match(text.strip())
        if not m:
            raise BlobRefError(f"not a substrate reference: {text!r} (want sha256:<64 hex>:<size>)")
        return cls(algo=m["algo"], digest=m["digest"], size=int(m["size"]))

    def resolves(self, data: bytes) -> bool:
        """Does this blob actually satisfy the reference? Size first — it is the cheap disagreement."""
        return len(data) == self.size and sha256_hex(data) == self.digest
