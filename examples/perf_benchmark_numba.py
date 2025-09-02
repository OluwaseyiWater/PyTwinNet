from time import perf_counter
from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.visualization.heatmap_fast import sinr_heatmap_2d_fast

def run(res=600):
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(1000,1000,30)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode("gNB-1",(300,300,10),TransceiverProperties(32,5), metadata={"role":"gNB"}))
    net.add_node(WirelessNode("gNB-2",(700,700,10),TransceiverProperties(32,5), metadata={"role":"gNB"}))
    twin.network = net

    # warm-up (compiles Numba)
    sinr_heatmap_2d_fast(twin, "gNB-1", interferer_ids=["gNB-2"], xlim=(0,1000), ylim=(0,1000), resolution=200)

    t0 = perf_counter()
    _, Z = sinr_heatmap_2d_fast(twin, "gNB-1", interferer_ids=["gNB-2"], xlim=(0,1000), ylim=(0,1000), resolution=res)
    dt = perf_counter() - t0
    print(f"Numba test {res}x{res} -> {Z.shape} in {dt:.3f}s")

if __name__ == "__main__":
    run(300)
    run(600)
    run(900)
