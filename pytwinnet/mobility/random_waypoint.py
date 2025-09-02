
from __future__ import annotations
import random, math
from dataclasses import dataclass
from typing import Tuple, Optional
from ..core.node import WirelessNode
from ..physics.environment import Environment

@dataclass
class RandomWaypoint:
    env: Environment
    speed_range_mps: Tuple[float, float] = (0.5, 1.5)
    pause_time_s: float = 0.0
    seed: int = 0
    _rng: random.Random = None
    _target: Optional[Tuple[float, float, float]] = None
    _speed: float = 0.0
    _paused_until: float = 0.0
    _last_t: Optional[float] = None
    def __post_init__(self):
        self._rng = random.Random(self.seed)
    def _sample_waypoint(self) -> Tuple[float, float, float]:
        w, d, h = self.env.dimensions_m
        return (self._rng.uniform(0, w), self._rng.uniform(0, d), self._rng.uniform(0, h))
    def update(self, node: WirelessNode, timestamp: float) -> None:
        if self._last_t is None:
            self._last_t = timestamp
            self._target = self._sample_waypoint()
            self._speed = self._rng.uniform(*self.speed_range_mps)
            return
        dt = max(0.0, timestamp - self._last_t)
        self._last_t = timestamp
        if timestamp < self._paused_until:
            return
        x, y, z = node.position
        tx, ty, tz = self._target
        dx, dy, dz = tx - x, ty - y, tz - z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 1e-6:
            self._paused_until = timestamp + self.pause_time_s
            self._target = self._sample_waypoint()
            self._speed = self._rng.uniform(*self.speed_range_mps)
            return
        step = self._speed * dt
        if step >= dist:
            node.move_to((tx, ty, tz))
        else:
            nx = x + dx / dist * step
            ny = y + dy / dist * step
            nz = z + dz / dist * step
            node.move_to((nx, ny, nz))
