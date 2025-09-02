from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.optimization.objective import SumThroughputObjective
from pytwinnet.optimization.placement_parallel import ParallelPlacementGrid

def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(300, 300, 30)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(20, 20, 10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                              metadata={"role":"gNB"}))
    for i, pos in enumerate([(60,80,1.5),(120,90,1.5),(220,150,1.5),(260,240,1.5)]):
        net.add_node(WirelessNode(f"UE-{i+1}", position=pos))
    twin.network = net

    obj = SumThroughputObjective(tx_id="gNB-1", efficiency=0.75)
    grid_x = [50, 100, 150, 200, 250]
    grid_y = [50, 100, 150, 200, 250]

    optimizer = ParallelPlacementGrid(grid_x=grid_x, grid_y=grid_y, fixed_z=10.0, max_workers=0)
    res = optimizer.optimize(twin, obj, node_ids=["gNB-1"])
    print("Best:", res["best_positions"], "score=", f"{res['best_score']:.2e}", "evals=", res["evaluations"])

if __name__ == "__main__":
    main()
