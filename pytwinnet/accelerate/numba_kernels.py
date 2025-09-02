from __future__ import annotations
import math
import numpy as np

try:
    from numba import njit, prange
    HAVE_NUMBA = True
except Exception:  # pragma: no cover
    HAVE_NUMBA = False
    def njit(*args, **kwargs):
        def deco(f): return f
        return deco
    def prange(x): return range(x)

@njit(cache=True, fastmath=True, nogil=True, parallel=True)
def _pairwise_dist_numba(tx_xyz: np.ndarray, rx_xyz: np.ndarray) -> np.ndarray:
    T = tx_xyz.shape[0]
    R = rx_xyz.shape[0]
    out = np.empty((T, R), dtype=np.float64)
    for i in prange(T):
        tx0 = tx_xyz[i, 0]; tx1 = tx_xyz[i, 1]; tx2 = tx_xyz[i, 2]
        for j in range(R):
            dx = tx0 - rx_xyz[j, 0]
            dy = tx1 - rx_xyz[j, 1]
            dz = tx2 - rx_xyz[j, 2]
            out[i, j] = math.sqrt(dx*dx + dy*dy + dz*dz)
    return out

@njit(cache=True, fastmath=True, nogil=True, parallel=True)
def fspl_matrix_db_numba(tx_xyz: np.ndarray, rx_xyz: np.ndarray, f_mhz: float) -> np.ndarray:
    d_m = _pairwise_dist_numba(tx_xyz, rx_xyz)
    T = d_m.shape[0]; R = d_m.shape[1]
    out = np.empty((T, R), dtype=np.float64)
    c2 = 20.0 * math.log10(f_mhz) + 32.44
    for i in prange(T):
        for j in range(R):
            dk = max(d_m[i, j], 1e-3) / 1_000.0
            out[i, j] = 20.0 * math.log10(dk) + c2
    return out

@njit(cache=True, fastmath=True, nogil=True, parallel=True)
def sinr_db_from_rsrp_matrix_numba(
    rsrp_dbm: np.ndarray,  # (T,R)
    serving_tx_idx: np.ndarray,  # (R,)
    noise_dbm: np.ndarray,       # (R,)
) -> np.ndarray:
    T = rsrp_dbm.shape[0]
    R = rsrp_dbm.shape[1]
    out = np.empty(R, dtype=np.float64)
    for j in prange(R):
        # sum powers in mW
        total_mw = 0.0
        for i in range(T):
            total_mw += 10.0 ** (rsrp_dbm[i, j] / 10.0)
        sig_mw = 10.0 ** (rsrp_dbm[serving_tx_idx[j], j] / 10.0)
        noi_mw = 10.0 ** (noise_dbm[j] / 10.0)
        denom = max(total_mw - sig_mw + noi_mw, 1e-30)
        sinr_lin = sig_mw / denom
        out[j] = 10.0 * math.log10(sinr_lin)
    return out
