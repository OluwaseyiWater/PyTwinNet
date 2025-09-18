from __future__ import annotations
import math, hashlib, random
from dataclasses import dataclass
from typing import Optional
from .propagation import PropagationModel
from .environment import Environment
from ..core.node import WirelessNode

def _pair_seed(base_seed: int, a: str, b: str, epoch: Optional[int]) -> int:
    s = f"{base_seed}|{a}|{b}|{epoch if epoch is not None else 'static'}"
    h = hashlib.sha256(s.encode()).hexdigest()
    return int(h[:16], 16)  # 64-bit

@dataclass
class ShadowedModel(PropagationModel):
    """
    Wraps a base propagation model and adds *log-normal shadowing* (Gaussian in dB).
    Shadowing is deterministic per (tx, rx, epoch) for reproducibility. Change 'epoch'
    (int) to refresh the samples (e.g., per-drop or per-time-slot).
    """
    base: PropagationModel
    sigma_db: float = 6.0
    seed: int = 0
    epoch: Optional[int] = None

    def set_epoch(self, epoch: Optional[int]) -> None:
        self.epoch = epoch

    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float:
        pl = self.base.calculate_path_loss(tx, rx, environment)
        rng = random.Random(_pair_seed(self.seed, tx.node_id, rx.node_id, self.epoch))
        shad = rng.gauss(0.0, self.sigma_db)
        return pl + shad

@dataclass
class FadedModel(PropagationModel):
    """
    Wraps a base model and adds *small-scale fading* (Rayleigh or Rician) as an extra
    dB term: PL_faded = PL + fading_loss_db where fading_loss_db = -10*log10(|h|^2).
    Fading is deterministic per (tx, rx, epoch). Change 'epoch' to re-sample.
    """
    base: PropagationModel
    kind: str = "rayleigh"     # "rayleigh" or "rician"
    K_dB: float = 6.0          # Rician K-factor (dB) if kind == "rician"
    seed: int = 0
    epoch: Optional[int] = None

    def set_epoch(self, epoch: Optional[int]) -> None:
        self.epoch = epoch

    @staticmethod
    def _rayleigh_gain(rng: random.Random) -> float:
        # |h|^2 ~ Exp(1)
        u = max(rng.random(), 1e-12)
        return -math.log(u)  # exponential(1)

    @staticmethod
    def _rician_gain(rng: random.Random, K_linear: float) -> float:
        # h = s + n, with s = sqrt(K/(K+1)), n ~ CN(0, 1/(K+1))
        sigma = math.sqrt(1.0 / (2.0 * (K_linear + 1.0)))  # per real/imag
        s = math.sqrt(K_linear / (K_linear + 1.0))
        xr = rng.gauss(s, sigma)
        xi = rng.gauss(0.0, sigma)
        return xr * xr + xi * xi  # |h|^2

    def calculate_path_loss(self, tx: WirelessNode, rx: WirelessNode, environment: Environment) -> float:
        pl = self.base.calculate_path_loss(tx, rx, environment)
        rng = random.Random(_pair_seed(self.seed, tx.node_id, rx.node_id, self.epoch))
        if self.kind.lower().startswith("ray"):
            g = self._rayleigh_gain(rng)
        else:
            K_lin = 10 ** (self.K_dB / 10.0)
            g = self._rician_gain(rng, K_lin)
        # fading loss in dB (negative gain -> positive extra loss)
        fading_loss_db = -10.0 * math.log10(max(g, 1e-12))
        return pl + fading_loss_db
