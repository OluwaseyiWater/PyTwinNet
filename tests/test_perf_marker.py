import time, pytest
from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.visualization.heatmap_fast import sinr_heatmap_2d_fast

@pytest.mark.perf
def test_heatmap_perf_smoke():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(400,400,30)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode("gNB-1",(100,100,10),TransceiverProperties(32,5),metadata={"role":"gNB"}))
    net.add_node(WirelessNode("gNB-2",(300,300,10),TransceiverProperties(32,5),metadata={"role":"gNB"}))
    twin.network = net

    t0 = time.time()
    _, _ = sinr_heatmap_2d_fast(twin, "gNB-1", interferer_ids=["gNB-2"], resolution=250, show=False)
    dt = time.time() - t0
    assert dt < 2.0
