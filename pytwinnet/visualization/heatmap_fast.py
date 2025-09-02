from __future__ import annotations
from typing import Tuple, List, Optional
import numpy as np
import matplotlib.pyplot as plt

from ..core.digital_twin import DigitalTwin
from ..physics.batch import path_loss_matrix
from ..accelerate.vectorized import (
    rsrp_matrix_dbm,
    noise_dbm_vector,
    sinr_db_from_rsrp_matrix,
)

def sinr_heatmap_2d_fast(
    twin: DigitalTwin,
    tx_id: str,
    interferer_ids: Optional[List[str]] = None,
    plane_z: float = 1.5,
    xlim: Tuple[float, float] = (0.0, 100.0),
    ylim: Tuple[float, float] = (0.0, 100.0),
    resolution: int = 200,
    bandwidth_hz: float = 20e6,
    noise_figure_db: float = 7.0,
    show: bool = False,
):
    """
    Vectorized SINR heatmap for any PropagationModel.

    - Uses fast, batch path-loss where available.
    - Falls back to a low-overhead scalar loop that reuses node objects.
    """
    assert twin.propagation_model is not None and twin.environment is not None

    tx = twin.network.get_node_by_id(tx_id)
    assert tx is not None, f"Transmitter {tx_id} not found"

    interferers = [twin.network.get_node_by_id(i) for i in (interferer_ids or [])]
    interferers = [n for n in interferers if n is not None]
    txs = [tx] + interferers
    T = len(txs)

    # Grid (R = resolution^2)
    xs = np.linspace(*xlim, resolution)
    ys = np.linspace(*ylim, resolution)
    X, Y = np.meshgrid(xs, ys)
    R = resolution * resolution
    rx_xyz = np.column_stack([X.reshape(-1), Y.reshape(-1), np.full(R, plane_z)])

    # TX arrays for link budget
    tx_dbm = np.array([n.transceiver_properties.transmit_power_dbm for n in txs], dtype=float)
    gt_dbi = np.array([n.transceiver_properties.antenna_gain_dbi for n in txs], dtype=float)
    gr_dbi = np.zeros(R, dtype=float)  # isotropic "probes" on the plane

    # Path-loss matrix (T,R) via generic fast helper
    pl_db = path_loss_matrix(twin, txs, rx_xyz)

    # RSRP per TX-RX
    rsrp_dbm = rsrp_matrix_dbm(tx_dbm, gt_dbi, gr_dbi, pl_db)

    # Assume first TX is serving; the rest are co-channel interferers
    serving_idx = np.zeros(R, dtype=int)
    noise = noise_dbm_vector(bandwidth_hz, noise_figure_db=noise_figure_db) * np.ones(R)
    sinr = sinr_db_from_rsrp_matrix(rsrp_dbm, serving_idx, noise).reshape(resolution, resolution)

    # Plot
    fig, ax = plt.subplots()
    im = ax.imshow(
        sinr, origin="lower",
        extent=(xlim[0], xlim[1], ylim[0], ylim[1]),
        aspect="auto",
    )
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.set_title(f"Fast SINR Heatmap (dB) - {tx_id} (+{T-1} interferers)")
    fig.colorbar(im, ax=ax, label="SINR (dB)")
    if show:
        plt.show()
    return ax, sinr
