from __future__ import annotations
from typing import List

def round_robin_schedule(ue_ids: List[str], rb_count: int) -> List[str]:
    if not ue_ids:
        return []
    out: List[str] = []
    i = 0
    for _ in range(rb_count):
        out.append(ue_ids[i])
        i = (i + 1) % len(ue_ids)
    return out
