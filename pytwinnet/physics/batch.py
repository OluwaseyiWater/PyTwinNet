from __future__ import annotations
from typing import List, Iterable
import numpy as np
from ..core.node import WirelessNode
from ..core.digital_twin import DigitalTwin
from .propagation import PropagationModel, FreeSpacePathLoss
from ..accelerate.vectorized import fspl_matrix_db

def path_loss_matrix(
    twin: DigitalTwin,
    tx_nodes: List[WirelessNode],
    rx_positions: np.ndarray,  # (R,3) float
) -> np.ndarray:
    """
    Return PL (dB) matrix of shape (T,R) for arbitrary PropagationModel.

    Fast paths:
      - If model is FreeSpacePathLoss -> fully vectorized (no Python loops).
      - If model implements an optional `calculate_path_loss_batch(tx_nodes, rx_positions, env)`
        it will be used directly (hook for future custom vectorized models).

    Fallback:
      - Reuse a single RX WirelessNode and update its .position per point to avoid
        per-point allocations. This is still scalar but much faster than constructing
        nodes in a tight loop.
    """
    pm: PropagationModel = twin.propagation_model
    env = twin.environment
    assert pm is not None and env is not None

    T = len(tx_nodes)
    R = int(rx_positions.shape[0])
    if T == 0 or R == 0:
        return np.zeros((T, R), dtype=float)

    # Fast path: pure FSPL
    if isinstance(pm, FreeSpacePathLoss):
        tx_xyz = np.array([tx.position for tx in tx_nodes], dtype=float)  # (T,3)
        f_hz = tx_nodes[0].transceiver_properties.carrier_frequency_hz
        return fspl_matrix_db(tx_xyz, rx_positions, f_hz)

    # Optional vectorized API hook
    if hasattr(pm, "calculate_path_loss_batch"):
        return pm.calculate_path_loss_batch(tx_nodes, rx_positions, env)  

    # Scalar fallback (minimize allocations)
    pl = np.empty((T, R), dtype=float)
    rx = WirelessNode("__rx__", position=(0.0, 0.0, 0.0))
    for j in range(R):
        # update one shared RX node position
        rx.position = (float(rx_positions[j, 0]), float(rx_positions[j, 1]), float(rx_positions[j, 2]))
        for i, tx in enumerate(tx_nodes):
            pl[i, j] = pm.calculate_path_loss(tx, rx, env)
    return pl
