from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.optimization.objective import SumThroughputObjective
from pytwinnet.optimization.placement import PlacementRandomSearchOptimizer, PlacementGridOptimizer

def build_twin():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(300,300,30)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(50,50,10),
                   transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                   metadata={"role":"gNB"}))
    for i, pos in enumerate([(60,70,1.5),(120,120,1.5),(200,210,1.5),(260,240,1.5)]):
        net.add_node(WirelessNode(f"UE-{i+1}", position=pos))
    twin.network = net
    return twin

def main():
    twin = build_twin()
    obj = SumThroughputObjective(tx_id="gNB-1", efficiency=0.75)

    rand_opt = PlacementRandomSearchOptimizer(bounds=((0,300),(0,300)), samples=200, fixed_z=10)
    res_r = rand_opt.optimize(twin, obj, node_ids=["gNB-1"])
    print("Random placement:", res_r["best_positions"], "score=", f"{res_r['best_score']:.2e}")

    grid = [50, 100, 150, 200, 250]
    grid_opt = PlacementGridOptimizer(grid_x=grid, grid_y=grid, fixed_z=10)
    res_g = grid_opt.optimize(twin, obj, node_ids=["gNB-1"])
    print("Grid placement:", res_g["best_positions"], "score=", f"{res_g['best_score']:.2e}")

if __name__ == "__main__":
    main()
