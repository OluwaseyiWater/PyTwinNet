from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.handover import HandoverController

def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(300,300,30)))
    twin.set_propagation_model(FreeSpacePathLoss())

    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(50,150,10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                              metadata={"role":"gNB"}))
    net.add_node(WirelessNode("gNB-2", position=(250,150,10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                              metadata={"role":"gNB"}))
    net.add_node(WirelessNode("UE-1", position=(60,150,1.5)))
    twin.network = net

    ho = HandoverController(hysteresis_db=3.0, time_to_trigger_s=0.64)
    serving = "gNB-1"
    t = 0.0
    for step in range(11):
        x = 60 + step * 20      # move east every step
        ue = twin.network.get_node_by_id("UE-1")
        ue.move_to((x, 150, 1.5))
        serving_new = ho.step(twin, "UE-1", serving, timestamp_s=t)
        print(f"t={t:.2f}s, UE-1 at x={x}, serving={serving} -> {serving_new}")
        serving = serving_new
        t += 0.2

if __name__ == "__main__":
    main()
