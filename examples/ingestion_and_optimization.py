"""
Ingestion + Optimization demo for PyTwinNet.

- Build a twin with gNB + 2 UEs
- Apply a few mock real-time updates (node movement)
- Generate traffic to create a naive "throughput" signal
- Run SimpleGreedyOptimizer to improve the (toy) throughput objective
- Print path loss and final node states
"""

from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.simulation import Scenario, MoveNodeEvent, Simulator, TrafficGenerationEvent
from pytwinnet.ingestion import MockDataSource, RealTimeMonitor
from pytwinnet.optimization import SimpleGreedyOptimizer
from pytwinnet.optimization.objective import MaximizeThroughput


def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(200.0, 200.0, 30.0)))
    twin.set_propagation_model(FreeSpacePathLoss())

    # --- Build a simple network ---
    net = Network()
    net.add_node(WirelessNode(node_id="gNB-1", position=(0.0, 0.0, 10.0),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=30.0)))
    net.add_node(WirelessNode(node_id="UE-1", position=(10.0, 0.0, 1.5)))
    net.add_node(WirelessNode(node_id="UE-2", position=(0.0, 20.0, 1.5)))
    twin.network = net

    # --- Ingestion demo: move UEs a bit using mock updates ---
    source = MockDataSource(node_ids=["UE-1", "UE-2"], step_size_m=2.0, seed=42)
    source.connect()
    monitor = RealTimeMonitor(twin=twin, source=source)
    applied = monitor.poll_once()  # apply one batch of random small movements
    print(f"[Ingestion] Applied {applied} mock updates.")
    for n in twin.network.list_nodes():
        print(f"  {n.node_id} -> position={n.position}")

    # --- Generate some traffic (toy) ---
    scen = Scenario(duration_s=5.0)
    scen.add_event(TrafficGenerationEvent(timestamp=1.0, source_node="gNB-1", dest_node="UE-1", data_rate_mbps=5.0))
    scen.add_event(TrafficGenerationEvent(timestamp=2.0, source_node="gNB-1", dest_node="UE-2", data_rate_mbps=2.5))
    Simulator(twin).run(scenario=scen, copy_twin=False)  # mutate twin directly for demonstration

    # --- Compute path loss between gNB and each UE (FSPL) ---
    fspl = twin.propagation_model
    env = twin.environment
    gnb = twin.network.get_node_by_id("gNB-1")
    for ue_id in ["UE-1", "UE-2"]:
        ue = twin.network.get_node_by_id(ue_id)
        pl_db = fspl.calculate_path_loss(gnb, ue, env)
        print(f"[Physics] FSPL(gNB-1 -> {ue_id}) = {pl_db:.2f} dB")

    # --- Optimization: greedy improve 'MaximizeThroughput' (toy) ---
    opt = SimpleGreedyOptimizer(step_db=1.0, max_power_dbm=33.0, iterations=5)
    obj = MaximizeThroughput()
    summary = opt.optimize(twin, obj)
    print(f"[Optimization] best_score={summary['best_score']:.2f}, iterations={summary['iterations']}")
    print("  Power updates history (node_id, score):", summary["metadata"]["history"])

    # --- Final state ---
    for node in twin.network.list_nodes():
        print(f"{node.node_id}: position={node.position}, "
              f"tx_power={node.transceiver_properties.transmit_power_dbm:.1f} dBm, "
              f"recv_traffic={node.metadata.get('received_traffic_mbps', 0.0)} Mbps")


if __name__ == "__main__":
    main()
