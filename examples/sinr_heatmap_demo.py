
from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.visualization import sinr_heatmap_2d

def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(200, 200, 20)))
    twin.set_propagation_model(FreeSpacePathLoss())
    net = Network()
    net.add_node(WirelessNode(node_id="gNB-1", position=(50.0, 50.0, 10.0),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=30.0, antenna_gain_dbi=5.0),
                              metadata={"role":"gNB"}))
    net.add_node(WirelessNode(node_id="gNB-2", position=(150.0, 150.0, 10.0),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=30.0, antenna_gain_dbi=5.0),
                              metadata={"role":"gNB"}))
    twin.network = net
    sinr_heatmap_2d(twin, tx_id="gNB-1", interferer_ids=["gNB-2"],
                    xlim=(0, 200), ylim=(0, 200), resolution=60, show=False)
    print("Generated SINR heatmap (not displayed in non-GUI env).")

if __name__ == "__main__":
    main()
