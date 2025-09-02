
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional, Callable
from ..core.digital_twin import DigitalTwin
from .base import DataSource
from .mock import MockNodeUpdate

@dataclass
class RealTimeMonitor:
    twin: DigitalTwin
    source: DataSource
    on_applied: Optional[Callable[[object], None]] = None
    def poll_once(self, updates: Iterable[object] | None = None) -> int:
        count = 0
        if updates is None:
            updates = self.source.read_data()
        for upd in updates:
            applied = self._apply_update(upd)
            if applied:
                count += 1
                if self.on_applied:
                    self.on_applied(upd)
        return count
    def _apply_update(self, update: object) -> bool:
        if isinstance(update, MockNodeUpdate):
            node = self.twin.network.get_node_by_id(update.node_id)
            if node:
                x, y, z = node.position
                dx, dy, dz = update.new_position
                node.move_to((x + dx, y + dy, z + dz))
                return True
            return False
        return False
