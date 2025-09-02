from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import numpy as np
from .objective import Objective
from ..accelerate.vectorized import (
    fspl_matrix_db, rsrp_matrix_dbm, noise_dbm_vector, sinr_db_from_rsrp_matrix, shannon_throughput_bps_vector
)

@dataclass
class ProportionalFairObjective(Objective):
    tx_id: str
    efficiency: float = 0.75
    rb_bandwidth_hz: float = 180e3
    noise_figure_db: float = 7.0
    avg_throughput_bps: Dict[str, float] | None = None

    def evaluate(self, twin) -> float:
        tx = twin.network.get_node_by_id(self.tx_id)
        ues = [n for n in twin.network if n.node_id != self.tx_id]
        if not tx or not ues: return -1e9
        tx_xyz = np.array([tx.position], float)
        ue_xyz = np.array([u.position for u in ues], float)
        pl = fspl_matrix_db(tx_xyz, ue_xyz, tx.transceiver_properties.carrier_frequency_hz)
        rsrp = rsrp_matrix_dbm(
            np.array([tx.transceiver_properties.transmit_power_dbm]),
            np.array([tx.transceiver_properties.antenna_gain_dbi]),
            np.array([u.transceiver_properties.antenna_gain_dbi for u in ues]),
            pl,
        )[0]
        noise = noise_dbm_vector(self.rb_bandwidth_hz, noise_figure_db=self.noise_figure_db) * np.ones(len(ues))
        sinr = sinr_db_from_rsrp_matrix(rsrp[None, :], np.zeros(len(ues), dtype=int), noise)
        thr = shannon_throughput_bps_vector(self.rb_bandwidth_hz, sinr, efficiency=self.efficiency)
        thr = np.maximum(thr, 1.0)
        return float(np.sum(np.log(thr)))

@dataclass
class CoveragePercentileObjective(Objective):
    tx_id: str
    percentile: float = 5.0
    bandwidth_hz: float = 20e6
    noise_figure_db: float = 7.0

    def evaluate(self, twin) -> float:
        tx = twin.network.get_node_by_id(self.tx_id)
        ues = [n for n in twin.network if n.node_id != self.tx_id]
        if not tx or not ues: return -1e9
        tx_xyz = np.array([tx.position], float)
        ue_xyz = np.array([u.position for u in ues], float)
        pl = fspl_matrix_db(tx_xyz, ue_xyz, tx.transceiver_properties.carrier_frequency_hz)
        rsrp = rsrp_matrix_dbm(
            np.array([tx.transceiver_properties.transmit_power_dbm]),
            np.array([tx.transceiver_properties.antenna_gain_dbi]),
            np.array([u.transceiver_properties.antenna_gain_dbi for u in ues]),
            pl,
        )[0]
        noise = noise_dbm_vector(self.bandwidth_hz, noise_figure_db=self.noise_figure_db) * np.ones(len(ues))
        sinr = sinr_db_from_rsrp_matrix(rsrp[None, :], np.zeros(len(ues), dtype=int), noise)
        return float(np.percentile(sinr, self.percentile))

@dataclass
class EnergyEfficiencyObjective(Objective):
    tx_id: str
    efficiency: float = 0.75
    bandwidth_hz: float = 20e6
    noise_figure_db: float = 7.0
    power_penalty: float = 1.0  # utility penalty per dBm

    def evaluate(self, twin) -> float:
        tx = twin.network.get_node_by_id(self.tx_id)
        ues = [n for n in twin.network if n.node_id != self.tx_id]
        if not tx or not ues: return -1e9
        tx_xyz = np.array([tx.position], float)
        ue_xyz = np.array([u.position for u in ues], float)
        pl = fspl_matrix_db(tx_xyz, ue_xyz, tx.transceiver_properties.carrier_frequency_hz)
        rsrp = rsrp_matrix_dbm(
            np.array([tx.transceiver_properties.transmit_power_dbm]),
            np.array([tx.transceiver_properties.antenna_gain_dbi]),
            np.array([u.transceiver_properties.antenna_gain_dbi for u in ues]),
            pl,
        )[0]
        noise = noise_dbm_vector(self.bandwidth_hz, noise_figure_db=self.noise_figure_db) * np.ones(len(ues))
        sinr = sinr_db_from_rsrp_matrix(rsrp[None, :], np.zeros(len(ues), dtype=int), noise)
        thr = shannon_throughput_bps_vector(self.bandwidth_hz, sinr, efficiency=self.efficiency)
        utility = float(np.sum(thr))
        penalty = self.power_penalty * tx.transceiver_properties.transmit_power_dbm
        return utility - penalty
