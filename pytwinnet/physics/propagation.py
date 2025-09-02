
from __future__ import annotations
import math
from abc import ABC, abstractmethod
from ..core.node import WirelessNode
from .environment import Environment

class PropagationModel(ABC):
    @abstractmethod
    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float: ...

class FreeSpacePathLoss(PropagationModel):
    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float:
        dx = tx.position[0] - rx.position[0]
        dy = tx.position[1] - rx.position[1]
        dz = tx.position[2] - rx.position[2]
        d_m = math.sqrt(dx*dx + dy*dy + dz*dz)
        d_km = max(d_m, 1e-3) / 1000.0
        f_mhz = max(tx.transceiver_properties.carrier_frequency_hz, 1.0) / 1e6
        return 20.0 * math.log10(d_km) + 20.0 * math.log10(f_mhz) + 32.44
