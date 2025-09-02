from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.physics.ris import RISPanel, RISAugmentedModel
from pytwinnet.physics.link_budget import rx_power_dbm

def main():
    base = FreeSpacePathLoss()
    ris = RISPanel(position=(100, 50, 10), gain_db=12.0)
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(200, 100, 30)))
    twin.set_propagation_model(RISAugmentedModel(base, ris, extra_loss_db=3.0))

    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(20, 50, 10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=30, antenna_gain_dbi=5),
                              metadata={"role":"gNB"}))
    net.add_node(WirelessNode("UE-1", position=(180, 50, 1.5)))
    twin.network = net

    pm = twin.propagation_model; env = twin.environment
    tx = twin.network.get_node_by_id("gNB-1")
    rx = twin.network.get_node_by_id("UE-1")

    pl_ris = pm.calculate_path_loss(tx, rx, env)
    prx_ris = rx_power_dbm(tx.transceiver_properties.transmit_power_dbm,
                           tx.transceiver_properties.antenna_gain_dbi,
                           rx.transceiver_properties.antenna_gain_dbi,
                           pl_ris)

    direct_pm = FreeSpacePathLoss()
    pl_direct = direct_pm.calculate_path_loss(tx, rx, env)
    prx_direct = rx_power_dbm(tx.transceiver_properties.transmit_power_dbm,
                              tx.transceiver_properties.antenna_gain_dbi,
                              rx.transceiver_properties.antenna_gain_dbi,
                              pl_direct)

    print(f"Direct-only RSRP: {prx_direct:.2f} dBm | RIS-augmented RSRP: {prx_ris:.2f} dBm (higher is better)")

if __name__ == "__main__":
    main()
