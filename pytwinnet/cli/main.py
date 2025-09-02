from __future__ import annotations
import argparse, json
from typing import Any, Dict
try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from e

from .. import DigitalTwin, Network, WirelessNode, TransceiverProperties
from ..physics import Environment, FreeSpacePathLoss
from ..physics.fading import ShadowedModel, FadedModel
from ..physics.ris_beam import SmartRISPanel, RISBeamModel
from ..visualization.heatmap_fast import sinr_heatmap_2d_fast
from ..optimization.objective import SumThroughputObjective
from ..optimization.placement import PlacementRandomSearchOptimizer, PlacementGridOptimizer

MODEL_MAP = {
    "fspl": FreeSpacePathLoss,
    "shadowed": ShadowedModel,
    "faded": FadedModel,
    "ris_beam": RISBeamModel,
}

OBJ_MAP = {
    "sum_throughput": SumThroughputObjective,
}

def build_twin(cfg: Dict[str, Any]) -> DigitalTwin:
    twin = DigitalTwin()
    env = cfg.get("environment", {})
    dims = env.get("dimensions_m", [100.0, 100.0, 30.0])
    twin.set_environment(Environment(dimensions_m=tuple(dims)))

    pm_cfg = cfg.get("propagation", {"model": "fspl"})
    model = pm_cfg.get("model", "fspl").lower()
    if model == "fspl":
        pm = FreeSpacePathLoss()
    elif model == "shadowed":
        base = FreeSpacePathLoss()
        pm = ShadowedModel(base, sigma_db=float(pm_cfg.get("sigma_db", 6.0)))
    elif model == "faded":
        base = FreeSpacePathLoss()
        pm = FadedModel(base, kind=str(pm_cfg.get("kind", "rayleigh")), K_dB=float(pm_cfg.get("K_dB", 6.0)))
    elif model == "ris_beam":
        base = FreeSpacePathLoss()
        ris_cfg = pm_cfg.get("ris", {})
        ris = SmartRISPanel(position=tuple(ris_cfg.get("position", [50.0, 50.0, 10.0])),
                            element_count=int(ris_cfg.get("element_count", 64)))
        pm = RISBeamModel(base, ris, extra_loss_db=float(pm_cfg.get("extra_loss_db", 3.0)))
    else:
        raise ValueError(f"Unknown propagation model: {model}")
    twin.set_propagation_model(pm)

    net = Network()
    for nd in cfg.get("nodes", []):
        role = nd.get("role", "")
        node = WirelessNode(
            node_id=str(nd["id"]),
            position=tuple(nd.get("position", [0.0, 0.0, 1.5])),
            transceiver_properties=TransceiverProperties(
                transmit_power_dbm=float(nd.get("tx_power_dbm", 20.0)),
                antenna_gain_dbi=float(nd.get("ant_gain_dbi", 0.0)),
                carrier_frequency_hz=float(nd.get("f_hz", 3.5e9)),
            ),
            metadata={"role": role} if role else {},
        )
        net.add_node(node)
    twin.network = net
    return twin

def apply_scenario(twin: DigitalTwin, cfg: Dict[str, Any]) -> None:
    # Minimal scenario support
    for ev in cfg.get("scenario", {}).get("events", []):
        et = ev.get("type")
        if et == "move_node":
            nid = ev["id"]; pos = tuple(ev["position"])
            n = twin.network.get_node_by_id(nid)
            if n: n.move_to(pos)
        elif et == "set_power":
            nid = ev["id"]; p = float(ev["tx_power_dbm"])
            n = twin.network.get_node_by_id(nid)
            if n: n.transceiver_properties.transmit_power_dbm = p
        elif et == "ris_beam":
            target = ev.get("target", None)
            pm = twin.propagation_model
            if hasattr(pm, "set_beam"):
                pm.set_beam(target)  # type: ignore

def run_optimizer(twin: DigitalTwin, cfg: Dict[str, Any]) -> Dict[str, Any]:
    opt_cfg = cfg.get("optimize")
    if not opt_cfg:
        return {}
    obj_cfg = opt_cfg.get("objective", {"type": "sum_throughput", "tx_id": None})
    obj_type = obj_cfg.get("type", "sum_throughput")
    if obj_type not in OBJ_MAP:
        raise ValueError(f"Unknown objective: {obj_type}")
    obj = OBJ_MAP[obj_type](**{k: v for k, v in obj_cfg.items() if k != "type"})

    method = opt_cfg.get("method", "random_search")
    targets = opt_cfg.get("node_ids", [])
    if method == "random_search":
        bounds = opt_cfg.get("bounds", [[0, 100], [0, 100]])
        samples = int(opt_cfg.get("samples", 100))
        opt = PlacementRandomSearchOptimizer(
            bounds=((bounds[0][0], bounds[0][1]), (bounds[1][0], bounds[1][1])),
            samples=samples,
            fixed_z=float(opt_cfg.get("fixed_z", 10.0)),
        )
        return opt.optimize(twin, obj, node_ids=targets)
    elif method == "grid":
        grid_x = opt_cfg.get("grid_x", [10, 20, 30])
        grid_y = opt_cfg.get("grid_y", [10, 20, 30])
        opt = PlacementGridOptimizer(grid_x=grid_x, grid_y=grid_y, fixed_z=float(opt_cfg.get("fixed_z", 10.0)))
        return opt.optimize(twin, obj, node_ids=targets)
    else:
        raise ValueError(f"Unknown optimize.method: {method}")

def maybe_heatmap(twin: DigitalTwin, cfg: Dict[str, Any]) -> str | None:
    vis = cfg.get("visualization", {})
    if not vis.get("heatmap", {}).get("enabled", False):
        return None
    h = vis["heatmap"]
    tx = h.get("tx_id")
    interfs = h.get("interferer_ids", [])
    xlim = tuple(h.get("xlim", [0, 100]))
    ylim = tuple(h.get("ylim", [0, 100]))
    res = int(h.get("resolution", 200))
    _, _ = sinr_heatmap_2d_fast(twin, tx_id=tx, interferer_ids=interfs, xlim=xlim, ylim=ylim, resolution=res, show=False)
    out = h.get("output", "heatmap.png")
    import matplotlib.pyplot as plt
    plt.savefig(out, bbox_inches="tight", dpi=150)
    return out

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="pytwinnet.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run", help="Run config-driven experiment")
    p_run.add_argument("config", help="Path to YAML config")

    args = parser.parse_args(argv)
    if args.cmd == "run":
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        twin = build_twin(cfg)
        apply_scenario(twin, cfg)
        opt_res = run_optimizer(twin, cfg)
        heat = maybe_heatmap(twin, cfg)
        report = {"optimize": opt_res, "heatmap": heat}
        out_json = cfg.get("output", "report.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Saved report -> {out_json}")
        if heat:
            print(f"Saved heatmap -> {heat}")
