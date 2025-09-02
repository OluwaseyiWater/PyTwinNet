from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.physics.ris_beam import SmartRISPanel, RISBeamModel
from pytwinnet.physics.link_budget import rx_power_dbm

def main():
    base = FreeSpacePathLoss()
    ris = SmartRISPanel(position=(100, 100, 10), element_count=128)
    model = RISBeamModel(base, ris, extra_loss_db=3.0)

    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(200,200,30)))
    twin.set_propagation_model(model)

    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(20, 100, 10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=30, antenna_gain_dbi=5),
                              metadata={"role":"gNB"}))
    net.add_node(WirelessNode("UE-1", position=(180, 100, 1.5)))
    net.add_node(WirelessNode("UE-2", position=(180, 130, 1.5)))
    twin.network = net

    pm = twin.propagation_model; env = twin.environment
    tx = net.get_node_by_id("gNB-1")

    # Steer RIS toward UE-1
    pm.set_beam("UE-1")
    for ue_id in ["UE-1","UE-2"]:
        rx = net.get_node_by_id(ue_id)
        pl = pm.calculate_path_loss(tx, rx, env)
        prx = rx_power_dbm(tx.transceiver_properties.transmit_power_dbm,
                           tx.transceiver_properties.antenna_gain_dbi, 0.0, pl)
        print(f"With beam=UE-1, RSRP at {ue_id}: {prx:.2f} dBm")

    # Steer RIS toward UE-2
    pm.set_beam("UE-2")
    for ue_id in ["UE-1","UE-2"]:
        rx = net.get_node_by_id(ue_id)
        pl = pm.calculate_path_loss(tx, rx, env)
        prx = rx_power_dbm(tx.transceiver_properties.transmit_power_dbm,
                           tx.transceiver_properties.antenna_gain_dbi, 0.0, pl)
        print(f"With beam=UE-2, RSRP at {ue_id}: {prx:.2f} dBm")

if __name__ == "__main__":
    main()
