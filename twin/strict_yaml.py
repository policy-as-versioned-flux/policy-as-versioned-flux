"""One YAML loader that refuses a duplicate mapping key, for every module that reads bytes
somebody else served.

`yaml.safe_load` silently keeps the LAST of two identical keys, so the file a human reviews is
not the file the validator read. Ticket 93 found that in the clock (`twin/derived_forecast.py`,
review F4: a visible `probability: 0.999` above a real `probability: 0.27` validated as 0.27) and
wrote `StrictLoader` there.

Eco-system ticket 31 re-check R1 found the same hole one level down, in sensor admission: the
closed key sets close the PARSED document, and a served admission record reading

    senses_role: <a person's name> <an email address>
    senses_role: platform-engineer

was ADMITTED with a green PASS, because the parser discarded the first line before any rule saw
it — including the value scan whose whole job is that email shape.

So the loader is lifted here rather than forked (ticket 102: no fork). `twin/derived_forecast.py`
imports `StrictLoader` from this module and keeps its own name for it, so nothing that referred
to `derived_forecast.StrictLoader` changes.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any

import yaml

#: The stable prefix `StrictLoader` puts on a duplicate-key error, so a caller can tell that
#: refusal apart from any other malformed YAML without matching PyYAML's own wording.
DUPLICATE_KEY = "duplicate key"


#: YAML's merge key. It legitimately appears more than once in one mapping and PyYAML removes it
#: in `flatten_mapping` before any of it reaches a document, so it is never a duplicate (F10).
MERGE_TAG = "tag:yaml.org,2002:merge"


class StrictLoader(yaml.SafeLoader):
    """`yaml.SafeLoader`, with a duplicate mapping key REFUSED instead of silently resolved.

    Two things it deliberately does NOT refuse (round-4 findings F10 and F13):

    * a **merge key**. The first cut constructed every key node before `flatten_mapping` had
      removed `<<`, so `<<: *a` was refused as a duplicate the moment a mapping carried two of
      them — and the refusal said the bytes were not YAML when they are.
    * a **complex key**. `key in seen` raised `TypeError` on an unhashable key, which surfaced as
      "not YAML this check will read (TypeError)" instead of PyYAML's own better message, and
      refused a complex key carrying no duplicate at all. Keys are compared by a hashable
      rendering, so a genuine duplicate complex key is still refused.
    """

    def construct_mapping(self, node: Any, deep: bool = False) -> dict[Any, Any]:
        seen: set[Any] = set()
        for key_node, _ in node.value:
            if getattr(key_node, "tag", None) == MERGE_TAG:
                continue
            key = self.construct_object(key_node, deep=deep)
            try:
                token = key if isinstance(key, Hashable) else repr(key)
            except Exception:  # noqa: BLE001 -- a key whose repr raises is still a key
                token = object()
            if token in seen:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    f"{DUPLICATE_KEY} {key!r}: PyYAML keeps the last, so the file a human reads "
                    f"is not the file this validator reads", key_node.start_mark)
            seen.add(token)
        return super().construct_mapping(node, deep=deep)


def duplicate_key(exc: BaseException) -> str | None:
    """The duplicated key this exception is about, or None if it is some other YAML fault."""
    text = str(exc)
    if DUPLICATE_KEY not in text:
        return None
    after = text.split(DUPLICATE_KEY, 1)[1].strip()
    return after.split(":", 1)[0].strip() or None
