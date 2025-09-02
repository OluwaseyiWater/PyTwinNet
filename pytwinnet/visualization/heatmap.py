
from __future__ import annotations
from typing import Tuple, List, Optional
import numpy as np
import matplotlib.pyplot as plt
from ..core.digital_twin import DigitalTwin
from ..physics.link_budget import rx_power_dbm, noise_power_dbm, sinr_db
from ..core.node import WirelessNode

def sinr_heatmap_2d(
    twin: DigitalTwin,
    tx_id: str,
    interferer_ids: Optional[List[str]] = None,
    plane_z: float = 1.5,
    xlim: Tuple[float, float] = (0.0, 100.0),
    ylim: Tuple[float, float] = (0.0, 100.0),
    resolution: int = 100,
    bandwidth_hz: float = 20e6,
    noise_figure_db: float = 7.0,
    show: bool = False,
):
    assert twin.propagation_model is not None and twin.environment is not None
    pm = twin.propagation_model
    env = twin.environment
    tx = twin.network.get_node_by_id(tx_id)
    assert tx is not None, f"Transmitter {tx_id} not found"
    inter_nodes = [twin.network.get_node_by_id(i) for i in (interferer_ids or [])]
    inter_nodes = [n for n in inter_nodes if n is not None]

    xs = np.linspace(xlim[0], xlim[1], resolution)
    ys = np.linspace(ylim[0], ylim[1], resolution)
    X, Y = np.meshgrid(xs, ys)
    Z = np.zeros_like(X, dtype=float)

    txp = tx.transceiver_properties.transmit_power_dbm
    gt = tx.transceiver_properties.antenna_gain_dbi
    gr = 0.0
    noise_dbm = noise_power_dbm(290.0, bandwidth_hz, noise_figure_db=noise_figure_db)

    for i in range(resolution):
        for j in range(resolution):
            rx_pos = (X[i, j], Y[i, j], plane_z)
            rx = WirelessNode(node_id="__rx__", position=rx_pos)
            pl_db = pm.calculate_path_loss(tx, rx, env)
            s_dbm = rx_power_dbm(txp, gt, gr, pl_db)
            ints = []
            for ino in inter_nodes:
                pl_i = pm.calculate_path_loss(ino, rx, env)
                ints.append(rx_power_dbm(ino.transceiver_properties.transmit_power_dbm,
                                         ino.transceiver_properties.antenna_gain_dbi, gr, pl_i))
            Z[i, j] = sinr_db(s_dbm, interferers_dbm=ints, noise_dbm=noise_dbm)

    fig, ax = plt.subplots()
    im = ax.imshow(Z, origin="lower", extent=(xlim[0], xlim[1], ylim[0], ylim[1]), aspect="auto")
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)"); ax.set_title(f"SINR Heatmap (dB) - {tx_id}")
    fig.colorbar(im, ax=ax, label="SINR (dB)")
    if show: plt.show()
    return ax, Z
