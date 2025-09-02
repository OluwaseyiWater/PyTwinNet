from __future__ import annotations
from typing import Dict, List
from ..core.digital_twin import DigitalTwin
from ..physics.link_budget import rx_power_dbm
from ..physics.propagation import PropagationModel
from ..physics.environment import Environment

def max_rsrp_association(twin: DigitalTwin, tx_ids: List[str], ue_ids: List[str]) -> Dict[str, str]:
    """Associate each UE to the TX (gNB) with the strongest RSRP."""
    pm: PropagationModel = twin.propagation_model
    env: Environment = twin.environment
    out: Dict[str, str] = {}
    for ue_id in ue_ids:
        ue = twin.network.get_node_by_id(ue_id)
        best_tx, best_p = None, float("-inf")
        for tx_id in tx_ids:
            tx = twin.network.get_node_by_id(tx_id)
            pl_db = pm.calculate_path_loss(tx, ue, env)
            prx_dbm = rx_power_dbm(
                tx.transceiver_properties.transmit_power_dbm,
                tx.transceiver_properties.antenna_gain_dbi,
                ue.transceiver_properties.antenna_gain_dbi,
                pl_db,
            )
            if prx_dbm > best_p:
                best_p, best_tx = prx_dbm, tx_id
        if best_tx is not None:
            out[ue_id] = best_tx
    return out
