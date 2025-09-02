from __future__ import annotations
import numpy as np
from typing import Tuple, Optional


try:
    from .numba_kernels import HAVE_NUMBA, fspl_matrix_db_numba, sinr_db_from_rsrp_matrix_numba
except Exception:  # pragma: no cover
    HAVE_NUMBA = False
    fspl_matrix_db_numba = None
    sinr_db_from_rsrp_matrix_numba = None
# ---------- Geometry / FSPL ----------

def _pairwise_dist(tx_xyz: np.ndarray, rx_xyz: np.ndarray) -> np.ndarray:
    """
    tx_xyz: (T,3), rx_xyz: (R,3) -> (T,R) 3D distances (meters)
    """
    d = tx_xyz[:, None, :] - rx_xyz[None, :, :]
    return np.linalg.norm(d, axis=2)

def fspl_matrix_db(
    tx_xyz: np.ndarray, rx_xyz: np.ndarray, f_hz: np.ndarray | float
) -> np.ndarray:
    """
    Vectorized Free-Space Path Loss in dB: (T,R)
    If f_hz is scalar and Numba is available -> JIT kernel.
    """
    if np.isscalar(f_hz):
        f_mhz = float(f_hz) / 1e6
        if HAVE_NUMBA and fspl_matrix_db_numba is not None:
            # Numba prefers float64
            return fspl_matrix_db_numba(
                np.asarray(tx_xyz, dtype=np.float64),
                np.asarray(rx_xyz, dtype=np.float64),
                float(f_mhz),
            )
        # NumPy fallback
        d = tx_xyz[:, None, :] - rx_xyz[None, :, :]
        d_m = np.linalg.norm(d, axis=2)
        d_km = np.maximum(d_m, 1e-3) / 1e3
        return 20.0 * np.log10(d_km) + 20.0 * np.log10(f_mhz) + 32.44
    # Vector f_hz: use NumPy path
    d = tx_xyz[:, None, :] - rx_xyz[None, :, :]
    d_m = np.linalg.norm(d, axis=2)
    d_km = np.maximum(d_m, 1e-3) / 1e3
    f_mhz = np.asarray(f_hz, dtype=float) / 1e6  # (T,)
    return 20.0 * np.log10(d_km) + 20.0 * np.log10(f_mhz[:, None]) + 32.44


# ---------- Link budget (vectorized) ----------

def rsrp_matrix_dbm(
    tx_dbm: np.ndarray, gt_dbi: np.ndarray, gr_dbi: np.ndarray, pl_db: np.ndarray
) -> np.ndarray:
    """
    RSRP (received power) in dBm for all TX-RX pairs.
    tx_dbm, gt_dbi: (T,), gr_dbi: (R,), pl_db: (T,R)
    -> (T,R)
    """
    return tx_dbm[:, None] + gt_dbi[:, None] + gr_dbi[None, :] - pl_db

def noise_dbm_vector(
    bandwidth_hz: np.ndarray | float,
    temperature_k: float = 290.0,
    noise_figure_db: np.ndarray | float = 0.0,
) -> np.ndarray:
    """
    Vectorized thermal noise power (dBm).
    bandwidth_hz: scalar or (R,), noise_figure_db: scalar or (R,)
    -> (R,)
    """
    # -174 dBm/Hz at 290K baseline
    # Adjust for temperature linearly in power domain -> +10*log10(T/290)
    temp_adj_db = 10.0 * np.log10(np.asarray(temperature_k, dtype=float) / 290.0)
    bw = np.asarray(bandwidth_hz, dtype=float)
    nf = np.asarray(noise_figure_db, dtype=float)
    return -174.0 + temp_adj_db + 10.0 * np.log10(np.maximum(bw, 1.0)) + nf

def sinr_db_from_rsrp_matrix(
    rsrp_dbm: np.ndarray,  # (T,R)
    serving_tx_idx: np.ndarray,  # (R,)
    noise_dbm: np.ndarray,       # (R,)
) -> np.ndarray:
    if HAVE_NUMBA and sinr_db_from_rsrp_matrix_numba is not None:
        return sinr_db_from_rsrp_matrix_numba(
            np.asarray(rsrp_dbm, dtype=np.float64),
            np.asarray(serving_tx_idx, dtype=np.int64),
            np.asarray(noise_dbm, dtype=np.float64),
        )
    # NumPy fallback
    p_mw = 10 ** (rsrp_dbm / 10.0)
    total_mw = p_mw.sum(axis=0)
    sig_mw = p_mw[serving_tx_idx, np.arange(p_mw.shape[1])]
    noi_mw = 10 ** (noise_dbm / 10.0)
    sinr_lin = sig_mw / np.maximum(total_mw - sig_mw + noi_mw, 1e-30)
    return 10.0 * np.log10(sinr_lin)


def shannon_throughput_bps_vector(
    bandwidth_hz: np.ndarray | float,
    sinr_db: np.ndarray,              # (R,)
    efficiency: float = 1.0,
) -> np.ndarray:
    """
    Vectorized Shannon throughput per RX (bps).
    """
    bw = np.asarray(bandwidth_hz, dtype=float)
    sinr_lin = 10 ** (sinr_db / 10.0)
    return efficiency * bw * np.log2(1.0 + sinr_lin)
