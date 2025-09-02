from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.visualization.heatmap_fast import sinr_heatmap_2d_fast

def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(400, 400, 30)))
    twin.set_propagation_model(FreeSpacePathLoss())

    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(120, 150, 10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                              metadata={"role":"gNB"}))
    net.add_node(WirelessNode("gNB-2", position=(300, 250, 10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                              metadata={"role":"gNB"}))
    twin.network = net

    sinr_heatmap_2d_fast(
        twin, tx_id="gNB-1", interferer_ids=["gNB-2"],
        xlim=(0, 400), ylim=(0, 400), resolution=250, show=False
    )
    print("Computed fast heatmap at 250x250 resolution.")

if __name__ == "__main__":
    main()
