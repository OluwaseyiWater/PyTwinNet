
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Any

@dataclass
class TransceiverProperties:
    transmit_power_dbm: float = 20.0
    antenna_gain_dbi: float = 0.0
    carrier_frequency_hz: float = 2.4e9
    additional: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WirelessNode:
    node_id: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    transceiver_properties: TransceiverProperties = field(default_factory=TransceiverProperties)
    mobility_model: Optional[object] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def move_to(self, new_position: Tuple[float, float, float]) -> None:
        self.position = new_position

    def update_mobility(self, timestamp: float) -> None:
        if self.mobility_model and hasattr(self.mobility_model, "update"):
            self.mobility_model.update(self, timestamp)
