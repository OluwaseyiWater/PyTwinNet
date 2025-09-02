from __future__ import annotations
from typing import Dict, List
import numpy as np
from ..core.digital_twin import DigitalTwin
from ..accelerate.vectorized import fspl_matrix_db, rsrp_matrix_dbm, noise_dbm_vector, sinr_db_from_rsrp_matrix

def max_sinr_association(twin: DigitalTwin, tx_ids: List[str], ue_ids: List[str],
                         bandwidth_hz: float = 20e6, nf_db: float = 7.0,
                         bias_db: Dict[str, float] | None = None) -> Dict[str, str]:
    txs = [twin.network.get_node_by_id(t) for t in tx_ids]; txs = [t for t in txs if t]
    ues = [twin.network.get_node_by_id(u) for u in ue_ids]; ues = [u for u in ues if u]
    if not txs or not ues:
        return {}
    tx_xyz = np.array([t.position for t in txs], float)
    ue_xyz = np.array([u.position for u in ues], float)
    f = txs[0].transceiver_properties.carrier_frequency_hz
    pl = fspl_matrix_db(tx_xyz, ue_xyz, f)
    rsrp = rsrp_matrix_dbm(
        np.array([t.transceiver_properties.transmit_power_dbm for t in txs]),
        np.array([t.transceiver_properties.antenna_gain_dbi for t in txs]),
        np.array([u.transceiver_properties.antenna_gain_dbi for u in ues]),
        pl,
    )
    if bias_db:
        for i, t in enumerate(txs):
            rsrp[i, :] += float(bias_db.get(t.node_id, 0.0))

    noise = noise_dbm_vector(bandwidth_hz, noise_figure_db=nf_db) * np.ones(len(ues))
    best: Dict[str, str] = {}
    for j in range(len(ues)):
        sinr_per_tx = []
        for i in range(len(txs)):
            sidx = np.array([i], dtype=int)
            val = sinr_db_from_rsrp_matrix(rsrp[:, j][:, None], sidx, noise[j:j+1])[0]
            sinr_per_tx.append(val)
        best_tx = int(np.argmax(sinr_per_tx))
        best[ues[j].node_id] = txs[best_tx].node_id
    return best
