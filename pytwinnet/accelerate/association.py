from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple
from ..core.digital_twin import DigitalTwin
from ..core.node import WirelessNode
from ..physics.propagation import PropagationModel
from ..physics.environment import Environment
from .vectorized import fspl_matrix_db, rsrp_matrix_dbm

def _stack_positions(nodes: List[WirelessNode]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    xyz = np.array([n.position for n in nodes], dtype=float)   # (N,3)
    pw = np.array([n.transceiver_properties.transmit_power_dbm for n in nodes], dtype=float)
    g  = np.array([n.transceiver_properties.antenna_gain_dbi for n in nodes], dtype=float)
    return xyz, pw, g

def max_rsrp_association_vectorized(
    twin: DigitalTwin, tx_ids: List[str], ue_ids: List[str]
) -> Dict[str, str]:
    """
    Vectorized max-RSRP association. Much faster than per-pair loops for large sets.
    """
    pm: PropagationModel = twin.propagation_model
    env: Environment = twin.environment
    assert pm is not None and env is not None

    txs = [twin.network.get_node_by_id(t) for t in tx_ids]
    ues = [twin.network.get_node_by_id(u) for u in ue_ids]
    txs = [t for t in txs if t is not None]
    ues = [u for u in ues if u is not None]
    if not txs or not ues:
        return {}

    tx_xyz, tx_dbm, gt_dbi = _stack_positions(txs)
    ue_xyz, _, gr_dbi = _stack_positions(ues)
    f_hz = txs[0].transceiver_properties.carrier_frequency_hz  # assume same for now

    # Build PL matrix via underlying scalar model by matching FSPL formula for speed.
    # If pm is not FSPL, we fall back to slow path.
    from ..physics.propagation import FreeSpacePathLoss
    if isinstance(pm, FreeSpacePathLoss):
        pl_db = fspl_matrix_db(tx_xyz, ue_xyz, f_hz)  # (T,R)
    else:
        # Slow fallback (still vectorizable with numba in future)
        import numpy as np
        pl_db = np.zeros((len(txs), len(ues)), dtype=float)
        for i, tx in enumerate(txs):
            for j, rx in enumerate(ues):
                pl_db[i, j] = pm.calculate_path_loss(tx, rx, env)

    rsrp_dbm = rsrp_matrix_dbm(tx_dbm, gt_dbi, gr_dbi, pl_db)  # (T,R)
    best_tx_idx = rsrp_dbm.argmax(axis=0)                      # (R,)
    mapping = {ues[j].node_id: txs[i].node_id for j, i in enumerate(best_tx_idx)}
    return mapping
