from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.optimization.objective import SumThroughputObjective
from pytwinnet.optimization.bayesopt import SimpleBayesOpt

def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(300,300,30)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode("gNB-1",(50,50,10),TransceiverProperties(32,5), metadata={"role":"gNB"}))
    for i, pos in enumerate([(60,80,1.5),(120,90,1.5),(220,150,1.5),(260,240,1.5)]):
        net.add_node(WirelessNode(f"UE-{i+1}", position=pos))
    twin.network = net

    obj = SumThroughputObjective(tx_id="gNB-1", efficiency=0.75)

    def evaluate_xy(xy):
        x, y = xy
        sim = twin.snapshot()
        sim.network.get_node_by_id("gNB-1").move_to((float(x), float(y), 10.0))
        return obj.evaluate(sim)

    bo = SimpleBayesOpt(bounds=[(0,300),(0,300)], init_points=8, iters=24, lengthscale=80.0, variance=1.0, seed=0)
    res = bo.run(evaluate_xy)
    print("BO best:", res)

if __name__ == "__main__":
    main()
