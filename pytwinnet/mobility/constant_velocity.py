
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
from ..core.node import WirelessNode

@dataclass
class ConstantVelocity:
    velocity_mps: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    start_time: float = 0.0
    _last_t: Optional[float] = None
    def update(self, node: WirelessNode, timestamp: float) -> None:
        if self._last_t is None:
            self._last_t = timestamp
            return
        dt = max(0.0, timestamp - self._last_t)
        self._last_t = timestamp
        x, y, z = node.position
        vx, vy, vz = self.velocity_mps
        node.move_to((x + vx * dt, y + vy * dt, z + vz * dt))
