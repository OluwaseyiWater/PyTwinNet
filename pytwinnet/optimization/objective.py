
from __future__ import annotations
from abc import ABC, abstractmethod
from ..core.digital_twin import DigitalTwin
from ..physics.link_budget import rx_power_dbm, noise_power_dbm, sinr_db, shannon_throughput_bps
from ..physics.propagation import PropagationModel
from ..physics.environment import Environment

class Objective(ABC):
    @abstractmethod
    def evaluate(self, twin: DigitalTwin) -> float: ...

class MaximizeThroughput(Objective):
    def evaluate(self, twin: DigitalTwin) -> float:
        total = 0.0
        for node in twin.network:
            total += float(node.metadata.get("received_traffic_mbps", 0.0))
        return total

class MinimizePowerConsumption(Objective):
    def evaluate(self, twin: DigitalTwin) -> float:
        total_power = 0.0
        for node in twin.network:
            total_power += float(node.transceiver_properties.transmit_power_dbm)
        return -total_power



class SumThroughputObjective(Objective):
    def __init__(self, tx_id: str, efficiency: float = 1.0):
        self.tx_id = tx_id
        self.efficiency = efficiency
    def evaluate(self, twin: DigitalTwin) -> float:
        if twin.propagation_model is None or twin.environment is None:
            return 0.0
        tx = twin.network.get_node_by_id(self.tx_id)
        if tx is None:
            return 0.0
        pm: PropagationModel = twin.propagation_model
        env: Environment = twin.environment
        total = 0.0
        for rx in twin.network:
            if rx.node_id == self.tx_id:
                continue
            pl_db = pm.calculate_path_loss(tx, rx, env)
            txp = tx.transceiver_properties.transmit_power_dbm
            gt = tx.transceiver_properties.antenna_gain_dbi
            gr = rx.transceiver_properties.antenna_gain_dbi
            prx_dbm = rx_power_dbm(txp, gt, gr, pl_db)
            bw = float(rx.transceiver_properties.additional.get("bandwidth_hz", 20e6))
            nf = float(rx.transceiver_properties.additional.get("noise_figure_db", 7.0))
            n_dbm = noise_power_dbm(290.0, bw, nf)
            snr_db_val = sinr_db(prx_dbm, interferers_dbm=None, noise_dbm=n_dbm)
            thr = shannon_throughput_bps(bw, snr_db_val, efficiency=self.efficiency)
            total += thr
        return total
