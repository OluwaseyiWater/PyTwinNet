from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.handover import HandoverController

def test_ho_kpis():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(300,300,30)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode("gNB-1",(50,150,10),TransceiverProperties(32,5),metadata={"role":"gNB"}))
    net.add_node(WirelessNode("gNB-2",(250,150,10),TransceiverProperties(32,5),metadata={"role":"gNB"}))
    net.add_node(WirelessNode("UE-1",(60,150,1.5)))
    twin.network = net

    ho = HandoverController(hysteresis_db=0.0, time_to_trigger_s=0.0)
    ho.reset_logs()

    serving = "gNB-1"
    # initial decision
    serving = ho.step_logged(twin, "UE-1", serving, 0.0)

    # move clearly toward gNB-2 and allow time to pass
    ue = twin.network.get_node_by_id("UE-1")
    ue.move_to((280,150,1.5))                     # ← further than 260 to make the margin obvious
    serving = ho.step_logged(twin, "UE-1", serving, 0.2)

    # (Optional) one more check to ensure state settled
    serving = ho.step_logged(twin, "UE-1", serving, 0.3)

    k = ho.kpis()
    assert k["handover_count"] >= 1
