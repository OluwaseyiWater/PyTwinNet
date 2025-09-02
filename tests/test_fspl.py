
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.core.node import WirelessNode

def test_fspl_increases_with_distance():
    pm = FreeSpacePathLoss()
    env = Environment()
    tx = WirelessNode("tx", position=(0,0,0))
    rx1 = WirelessNode("rx1", position=(1,0,0))
    rx2 = WirelessNode("rx2", position=(10,0,0))
    pl1 = pm.calculate_path_loss(tx, rx1, env)
    pl2 = pm.calculate_path_loss(tx, rx2, env)
    assert pl2 > pl1
