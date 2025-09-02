from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from ..core.node import WirelessNode
from .environment import Environment
from .propagation import PropagationModel

@dataclass
class RISPanel:
    position: Tuple[float, float, float]
    gain_db: float = 10.0  # toy reflective gain

class RISAugmentedModel(PropagationModel):
    """
    Wrap a base PropagationModel and return the min of:
    - direct path loss
    - two-hop path loss via RIS: PL(tx->RIS) + PL(RIS->rx) - RIS_gain + extra_loss
    """
    def __init__(self, base: PropagationModel, ris: RISPanel, extra_loss_db: float = 3.0) -> None:
        self.base = base
        self.ris = ris
        self.extra_loss_db = extra_loss_db

    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float:
        direct = self.base.calculate_path_loss(tx, rx, environment)
        tx2ris = WirelessNode("__tmp_tx2ris__", position=self.ris.position)
        ris2rx = WirelessNode("__tmp_ris2rx__", position=self.ris.position)
        pl1 = self.base.calculate_path_loss(tx, tx2ris, environment)
        pl2 = self.base.calculate_path_loss(ris2rx, rx, environment)
        via_ris = pl1 + pl2 - self.ris.gain_db + self.extra_loss_db
        return min(direct, via_ris)
