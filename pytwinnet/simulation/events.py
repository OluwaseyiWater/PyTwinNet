
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from ..core.digital_twin import DigitalTwin

@dataclass(order=True)
class Event:
    timestamp: float
    def apply(self, twin: DigitalTwin) -> None:
        raise NotImplementedError

@dataclass(order=True)
class MoveNodeEvent(Event):
    node_id: str
    new_position: Tuple[float, float, float]
    def apply(self, twin: DigitalTwin) -> None:
        node = twin.network.get_node_by_id(self.node_id)
        if node:
            node.move_to(self.new_position)

@dataclass(order=True)
class TrafficGenerationEvent(Event):
    source_node: str
    dest_node: str
    data_rate_mbps: float
    def apply(self, twin: DigitalTwin) -> None:
        src = twin.network.get_node_by_id(self.source_node)
        dst = twin.network.get_node_by_id(self.dest_node)
        if src and dst:
            src.metadata["generated_traffic_mbps"] = src.metadata.get("generated_traffic_mbps", 0.0) + self.data_rate_mbps
            dst.metadata["received_traffic_mbps"] = dst.metadata.get("received_traffic_mbps", 0.0) + self.data_rate_mbps
