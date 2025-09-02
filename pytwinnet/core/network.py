
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, List
from .node import WirelessNode

@dataclass
class Network:
    nodes: Dict[str, WirelessNode] = field(default_factory=dict)
    def add_node(self, node: WirelessNode) -> None:
        self.nodes[node.node_id] = node
    def remove_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            del self.nodes[node_id]
    def get_node_by_id(self, node_id: str) -> Optional[WirelessNode]:
        return self.nodes.get(node_id)
    def list_nodes(self) -> List[WirelessNode]:
        return list(self.nodes.values())
    def __iter__(self) -> Iterable[WirelessNode]:
        return iter(self.nodes.values())
