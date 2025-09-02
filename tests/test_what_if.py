
from pytwinnet import DigitalTwin, Network, WirelessNode
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.simulation import Scenario, MoveNodeEvent, what_if

def test_what_if_snapshot_isolated():
    twin = DigitalTwin()
    twin.set_environment(Environment())
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode("UE-1", position=(0,0,0)))
    twin.network = net
    scen = Scenario(duration_s=1.0)
    scen.add_event(MoveNodeEvent(timestamp=0.5, node_id="UE-1", new_position=(10,0,0)))
    res = what_if(twin, scen)
    assert twin.network.get_node_by_id("UE-1").position == (0,0,0)
    assert res["twin"].network.get_node_by_id("UE-1").position == (10,0,0)
