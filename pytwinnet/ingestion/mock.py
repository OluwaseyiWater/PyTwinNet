
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Iterable, List, Tuple
from .base import DataSource

@dataclass
class MockNodeUpdate:
    node_id: str
    new_position: Tuple[float, float, float]

class MockDataSource(DataSource):
    def __init__(self, node_ids: List[str], step_size_m: float = 1.0, seed: int = 0) -> None:
        self.node_ids = node_ids
        self.step = step_size_m
        self.rng = random.Random(seed)
    def connect(self) -> None:
        return None
    def read_data(self) -> Iterable[MockNodeUpdate]:
        for nid in self.node_ids:
            dx = (self.rng.random() - 0.5) * 2.0 * self.step
            dy = (self.rng.random() - 0.5) * 2.0 * self.step
            dz = 0.0
            yield MockNodeUpdate(node_id=nid, new_position=(dx, dy, dz))
