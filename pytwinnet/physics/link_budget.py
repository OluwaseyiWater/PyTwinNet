
from __future__ import annotations
import math
from typing import Iterable, Optional

def db_to_linear(db: float) -> float:
    return 10 ** (db / 10.0)

def linear_to_db(x: float) -> float:
    return 10.0 * math.log10(max(x, 1e-30))

def rx_power_dbm(tx_power_dbm: float, tx_gain_dbi: float, rx_gain_dbi: float, path_loss_db: float) -> float:
    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - path_loss_db

def noise_power_dbm(temperature_k: float, bandwidth_hz: float, noise_figure_db: float = 0.0) -> float:
    ref_dbm_per_hz = -174.0 + linear_to_db(temperature_k / 290.0)
    return ref_dbm_per_hz + 10.0 * math.log10(max(bandwidth_hz, 1.0)) + noise_figure_db

def sinr_db(signal_dbm: float, interferers_dbm: Optional[Iterable[float]] = None, noise_dbm: float = -100.0) -> float:
    def db2mw(v): return 10 ** (v / 10.0)
    sig_mw = db2mw(signal_dbm)
    int_mw = sum(db2mw(p) for p in (interferers_dbm or []))
    noi_mw = db2mw(noise_dbm)
    return 10.0 * math.log10(sig_mw / (int_mw + noi_mw))

def shannon_throughput_bps(bandwidth_hz: float, sinr_db_value: float, efficiency: float = 1.0) -> float:
    sinr = 10 ** (sinr_db_value / 10.0)
    return efficiency * bandwidth_hz * math.log2(1.0 + sinr)
