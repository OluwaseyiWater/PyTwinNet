from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import math
from ..core.node import WirelessNode
from .environment import Environment
from .propagation import PropagationModel

@dataclass
class SmartRISPanel:
    """
    Toy RIS with a steerable mainlobe. Approximates array gain:
      mainlobe_gain_db  ~= 20*log10(N)
      sidelobe_gain_db  ~= mainlobe - 13 dB (typical)
    """
    position: Tuple[float, float, float]
    element_count: int = 64
    mainlobe_gain_db: Optional[float] = None
    sidelobe_gain_db: Optional[float] = None

    def __post_init__(self):
        if self.mainlobe_gain_db is None:
            self.mainlobe_gain_db = 20.0 * math.log10(max(self.element_count, 1))
        if self.sidelobe_gain_db is None:
            self.sidelobe_gain_db = self.mainlobe_gain_db - 13.0

class RISBeamModel(PropagationModel):
    """
    Wraps a base PropagationModel. For a configured target UE (by id), the RIS
    contributes mainlobe gain on the two-hop path; others see sidelobe gain.
    Effective path loss = min( direct, (tx->RIS + RIS->rx - gain + extra_loss_db) ).
    """
    def __init__(self, base: PropagationModel, ris: SmartRISPanel, extra_loss_db: float = 3.0) -> None:
        self.base = base
        self.ris = ris
        self.extra_loss_db = extra_loss_db
        self._beam_target_id: Optional[str] = None

    def set_beam(self, rx_node_id: Optional[str]) -> None:
        """Point mainlobe toward rx_node_id (or None for no specific target)."""
        self._beam_target_id = rx_node_id

    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float:
        direct = self.base.calculate_path_loss(tx, rx, environment)
        tmp1 = WirelessNode("__tmp_tx2ris__", position=self.ris.position)
        tmp2 = WirelessNode("__tmp_ris2rx__", position=self.ris.position)
        pl1 = self.base.calculate_path_loss(tx, tmp1, environment)
        pl2 = self.base.calculate_path_loss(tmp2, rx, environment)
        gain = self.ris.mainlobe_gain_db if (self._beam_target_id == rx.node_id) else self.ris.sidelobe_gain_db
        via = pl1 + pl2 - gain + self.extra_loss_db
        return min(direct, via)
