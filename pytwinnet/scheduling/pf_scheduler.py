from __future__ import annotations
from typing import Dict, List
from ..core.digital_twin import DigitalTwin
from ..physics.link_budget import rx_power_dbm, noise_power_dbm, sinr_db, shannon_throughput_bps

def _est_throughput_bps(twin: DigitalTwin, tx_id: str, ue_id: str,
                        bandwidth_hz: float, noise_figure_db: float) -> float:
    pm = twin.propagation_model; env = twin.environment
    tx = twin.network.get_node_by_id(tx_id); ue = twin.network.get_node_by_id(ue_id)
    pl_db = pm.calculate_path_loss(tx, ue, env)
    prx_dbm = rx_power_dbm(
        tx.transceiver_properties.transmit_power_dbm,
        tx.transceiver_properties.antenna_gain_dbi,
        ue.transceiver_properties.antenna_gain_dbi,
        pl_db,
    )
    n_dbm = noise_power_dbm(290.0, bandwidth_hz, noise_figure_db)
    s = sinr_db(prx_dbm, interferers_dbm=None, noise_dbm=n_dbm)
    return shannon_throughput_bps(bandwidth_hz, s, efficiency=0.75)

def proportional_fair_allocation(
    twin: DigitalTwin,
    association: Dict[str, str],
    rb_count: int = 50,
    rb_bandwidth_hz: float = 180e3,
    noise_figure_db: float = 7.0,
    avg_throughput_bps: Dict[str, float] | None = None,
) -> Dict[str, List[str]]:
    """Greedy PF: per TX, for each RB pick UE maximizing inst_rate / avg_rate."""
    if avg_throughput_bps is None:
        avg_throughput_bps = {}
    eps = 1e-6

    # group UEs per TX
    per_tx: Dict[str, List[str]] = {}
    for ue_id, tx_id in association.items():
        per_tx.setdefault(tx_id, []).append(ue_id)

    schedule: Dict[str, List[str]] = {tx_id: [] for tx_id in per_tx.keys()}
    for tx_id, ues in per_tx.items():
        if not ues:
            continue
        for _ in range(rb_count):
            best_ue, best_metric = None, float("-inf")
            for ue_id in ues:
                inst = _est_throughput_bps(twin, tx_id, ue_id, rb_bandwidth_hz, noise_figure_db)
                avg = avg_throughput_bps.get(ue_id, inst)  # cold-start
                metric = inst / max(avg, eps)
                if metric > best_metric:
                    best_metric, best_ue = metric, ue_id
            schedule[tx_id].append(best_ue)
    return schedule
