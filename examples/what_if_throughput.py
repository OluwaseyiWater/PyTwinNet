from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.simulation import Scenario, MoveNodeEvent, what_if
from pytwinnet.optimization.objective import SumThroughputObjective

def build_twin():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(300.0, 300.0, 30.0)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode(node_id="gNB-1", position=(0.0, 0.0, 10.0),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=30.0, antenna_gain_dbi=5.0)))
    for i, pos in enumerate([(30.0, 0.0, 1.5), (0.0, 40.0, 1.5), (25.0, 25.0, 1.5), (60.0, 50.0, 1.5)]):
        net.add_node(WirelessNode(node_id=f"UE-{i+1}", position=pos))
    twin.network = net
    return twin

def scenario_move_gnb(new_position):
    s = Scenario(duration_s=1.0)
    s.add_event(MoveNodeEvent(timestamp=0.5, node_id="gNB-1", new_position=new_position))
    return s

def main():
    twin = build_twin()
    obj = SumThroughputObjective(tx_id="gNB-1", efficiency=0.75)
    resA = what_if(twin, scenario_move_gnb((20.0, 20.0, 10.0)), objective=obj)
    resB = what_if(twin, scenario_move_gnb((80.0, 80.0, 10.0)), objective=obj)
    print("Candidate A score (bps):", f"{resA['score']:.2f}")
    print("Candidate B score (bps):", f"{resB['score']:.2f}")
    print("\nFinal positions for Candidate A:")
    for n in resA["twin"].network.list_nodes():
        print(f"  {n.node_id}: {n.position}")

if __name__ == "__main__":
    main()
