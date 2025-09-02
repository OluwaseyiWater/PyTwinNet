from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from ..core.digital_twin import DigitalTwin
from ..physics.link_budget import rx_power_dbm

@dataclass
class HandoverController:
    hysteresis_db: float = 3.0
    time_to_trigger_s: float = 0.64
    _cand: Dict[str, Dict[str, float]] = field(default_factory=dict)  # ue_id -> {candidate_tx, start_time}

    def step(self, twin: DigitalTwin, ue_id: str, current_tx_id: str, timestamp_s: float) -> str:
        pm = twin.propagation_model; env = twin.environment
        ue = twin.network.get_node_by_id(ue_id)
        cur = twin.network.get_node_by_id(current_tx_id)

        # current RSRP
        cur_pl = pm.calculate_path_loss(cur, ue, env)
        cur_rsrp = rx_power_dbm(
            cur.transceiver_properties.transmit_power_dbm,
            cur.transceiver_properties.antenna_gain_dbi,
            ue.transceiver_properties.antenna_gain_dbi,
            cur_pl,
        )

        # best neighbor RSRP among gNB/BS roles
        best_tx_id, best_rsrp = current_tx_id, cur_rsrp
        for tx in twin.network:
            if tx.node_id == current_tx_id:
                continue
            role = str(tx.metadata.get("role", "")).lower()
            if "gnb" not in role and "bs" not in role:
                continue
            pl = pm.calculate_path_loss(tx, ue, env)
            p = rx_power_dbm(
                tx.transceiver_properties.transmit_power_dbm,
                tx.transceiver_properties.antenna_gain_dbi,
                ue.transceiver_properties.antenna_gain_dbi,
                pl,
            )
            if p > best_rsrp:
                best_tx_id, best_rsrp = tx.node_id, p

        # hysteresis + TTT
        if best_rsrp >= cur_rsrp + self.hysteresis_db and best_tx_id != current_tx_id:
            rec = self._cand.get(ue_id)
            if rec is None or rec.get("candidate_tx") != best_tx_id:
                self._cand[ue_id] = {"candidate_tx": best_tx_id, "start_time": timestamp_s}
            else:
                if (timestamp_s - rec["start_time"]) >= self.time_to_trigger_s:
                    self._cand.pop(ue_id, None)
                    return best_tx_id
        else:
            self._cand.pop(ue_id, None)

        return current_tx_id
    
        # --- KPI logging helpers ---
    def reset_logs(self):
        self._log = {"events": [], "ping_pong": 0}

    def log_event(self, ue_id: str, from_tx: str, to_tx: str, t: float):
        if not hasattr(self, "_log"):
            self.reset_logs()
        self._log["events"].append({"t": t, "ue": ue_id, "from": from_tx, "to": to_tx})
        if len(self._log["events"]) >= 2:
            prev = self._log["events"][-2]
            if prev["ue"] == ue_id and prev["from"] == to_tx and prev["to"] == from_tx:
                self._log["ping_pong"] += 1

    def step_logged(self, twin, ue_id: str, current_tx_id: str, timestamp_s: float) -> str:
        new_tx = self.step(twin, ue_id, current_tx_id, timestamp_s)
        if new_tx != current_tx_id:
            self.log_event(ue_id, current_tx_id, new_tx, timestamp_s)
        return new_tx

    def kpis(self) -> dict:
        if not hasattr(self, "_log"):
            self.reset_logs()
        return {
            "handover_count": len(self._log["events"]),
            "ping_pong_count": self._log["ping_pong"],
        }

