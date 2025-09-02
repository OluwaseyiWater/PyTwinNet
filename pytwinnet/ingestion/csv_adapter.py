from __future__ import annotations
import csv
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator
from .base import DataSource
from ..core.digital_twin import DigitalTwin

@dataclass
class CSVPositionDataSource(DataSource):
    """CSV source for node positions.

    CSV (header required):
        timestamp_s,node_id,x,y,z
    """
    path: str

    def connect(self) -> None:
        return

    def read_data(self) -> Iterator[Dict]:
        with open(self.path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                yield {
                    "timestamp_s": float(row["timestamp_s"]),
                    "node_id": row["node_id"],
                    "position": (float(row["x"]), float(row["y"]), float(row["z"])),
                }

class ReplayMonitor:
    """Replay updates from a DataSource into a DigitalTwin (offline)."""
    def __init__(self, twin: DigitalTwin, source: DataSource) -> None:
        self.twin = twin
        self.source = source

    def run(self, speed: float = 1.0) -> int:
        updates = 0
        events = sorted(self.source.read_data(), key=lambda d: d.get("timestamp_s", 0.0))
        for ev in events:
            nid = ev.get("node_id"); pos = ev.get("position")
            n = self.twin.network.get_node_by_id(nid)
            if n and pos:
                n.move_to(tuple(pos))
                updates += 1
        return updates

def rmse(a: Iterable[float], b: Iterable[float]) -> float:
    import math
    xs = list(a); ys = list(b)
    assert len(xs) == len(ys)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(xs, ys)) / len(xs))
