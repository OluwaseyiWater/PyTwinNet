
from pytwinnet.mobility import ConstantVelocity
from pytwinnet.core.node import WirelessNode

def test_constant_velocity_moves_node():
    n = WirelessNode("ue", position=(0,0,0))
    m = ConstantVelocity(velocity_mps=(1.0, 0.0, 0.0))
    n.mobility_model = m
    n.update_mobility(0.0)   # init
    n.update_mobility(2.0)   # after 2s
    assert abs(n.position[0] - 2.0) < 1e-6
