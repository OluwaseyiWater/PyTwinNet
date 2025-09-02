"""Basic example demonstrating PyTwinNet usage.

Steps
-----
1. Build a DigitalTwin with a simple Network (3 nodes).
2. Define a Scenario that moves one node.
3. Run the Simulator and print final node positions.
"""

from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.simulation import Scenario, MoveNodeEvent, Simulator


def main() -> None:
    # 1) Create twin and environment
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(200.0, 200.0, 30.0)))
    twin.set_propagation_model(FreeSpacePathLoss())

    # 2) Build a simple network
    net = Network()
    net.add_node(WirelessNode(node_id="gNB-1", position=(0.0, 0.0, 10.0),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=30.0)))
    net.add_node(WirelessNode(node_id="UE-1", position=(10.0, 0.0, 1.5)))
    net.add_node(WirelessNode(node_id="UE-2", position=(0.0, 20.0, 1.5)))
    twin.network = net

    # 3) Define a scenario: move UE-1
    scenario = Scenario(duration_s=10.0)
    scenario.add_event(MoveNodeEvent(timestamp=3.0, node_id="UE-1", new_position=(25.0, 5.0, 1.5)))

    # 4) Run simulator (on a snapshot to protect live twin)
    sim = Simulator(twin)
    final_twin = sim.run(scenario, copy_twin=True)

    # 5) Print final positions
    for node in final_twin.network.list_nodes():
        print(f"{node.node_id}: position={node.position}, tx_power={node.transceiver_properties.transmit_power_dbm:.1f} dBm")


if __name__ == "__main__":
    main()
