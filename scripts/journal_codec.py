"""Lossless Sheets journal payloads, including the two 1.1 wire formats."""
import base64
import hashlib
import json

from shared_state import StateError, canonical, require

CELL_BUDGET = 44000
PACKED_BYTES = 30000
PACKED_FORMAT = "cpe-journal/base64-utf8-v1"


def cell_units(text):
    """Conservative UTF-16 code-unit count, including supplementary characters."""
    return len(text.encode("utf-16-le")) // 2


def change_payloads(changes):
    groups, group, units = [], [], 0
    for change in changes:
        size = cell_units(canonical(change)) + 1
        if size + 128 > CELL_BUDGET:
            return packed_payloads(changes)
        if group and units + size + 128 > CELL_BUDGET:
            groups.append(group)
            group, units = [], 0
        group.append(change)
        units += size
    if group:
        groups.append(group)
    return [canonical({"part": n, "total": len(groups), "changes": batch})
            for n, batch in enumerate(groups, 1)]


def packed_payloads(changes):
    raw = canonical(changes).encode("utf-8")
    checksum = hashlib.sha256(raw).hexdigest()
    chunks = [raw[i:i + PACKED_BYTES] for i in range(0, len(raw), PACKED_BYTES)]
    return [canonical({"format": PACKED_FORMAT, "part": n, "total": len(chunks),
                       "sha256": checksum, "data": base64.b64encode(chunk).decode("ascii")})
            for n, chunk in enumerate(chunks, 1)]


def decode_event(rows):
    """Reassemble one PREPARED or CONFIRMED event; incomplete is never success."""
    require(bool(rows), "Missing journal event")
    payloads = [json.loads(row["changes_json"]) for row in rows]
    if len(payloads) == 1 and isinstance(payloads[0], list):
        return payloads[0]
    ordered = {}
    for payload in payloads:
        require(isinstance(payload, dict), "Malformed journal envelope")
        part, total = payload.get("part"), payload.get("total")
        require(type(part) is int and type(total) is int and total == len(rows)
                and 1 <= part <= total and part not in ordered,
                "Missing, duplicate or inconsistent journal part")
        ordered[part] = payload
    parts = [ordered[n] for n in range(1, len(rows) + 1)]
    if "changes" in parts[0]:
        require(all(set(p) == {"part", "total", "changes"} and isinstance(p["changes"], list)
                    for p in parts), "Mixed or malformed journal changes")
        return [change for p in parts for change in p["changes"]]
    checksum = parts[0].get("sha256")
    require(all(set(p) == {"format", "part", "total", "sha256", "data"}
                and p["format"] == PACKED_FORMAT and p["sha256"] == checksum
                and isinstance(p["data"], str) for p in parts), "Malformed packed event")
    try:
        raw = b"".join(base64.b64decode(p["data"], validate=True) for p in parts)
        require(hashlib.sha256(raw).hexdigest() == checksum, "Journal payload digest mismatch")
        value = json.loads(raw.decode("utf-8"))
    except (TypeError, ValueError) as error:
        raise StateError("Invalid packed journal payload") from error
    require(isinstance(value, list), "Journal payload must be a change list")
    return value
