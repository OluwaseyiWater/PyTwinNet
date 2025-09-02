from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.physics.fading import ShadowedModel, FadedModel
from pytwinnet.physics.link_budget import rx_power_dbm

def main():
    base = FreeSpacePathLoss()
    model = ShadowedModel(FadedModel(base, kind="rician", K_dB=6.0, seed=42), sigma_db=5.0, seed=7)
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(200,200,30)))
    twin.set_propagation_model(model)

    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(0,0,10),
                 transceiver_properties=TransceiverProperties(transmit_power_dbm=30, antenna_gain_dbi=5),
                 metadata={"role":"gNB"}))
    net.add_node(WirelessNode("UE-1", position=(120,80,1.5)))
    twin.network = net

    pm = twin.propagation_model; env = twin.environment
    tx = twin.network.get_node_by_id("gNB-1"); rx = twin.network.get_node_by_id("UE-1")

    # epoch 0
    pm.set_epoch(0)
    pl0 = pm.calculate_path_loss(tx, rx, env)
    p0 = rx_power_dbm(tx.transceiver_properties.transmit_power_dbm, tx.transceiver_properties.antenna_gain_dbi, 0.0, pl0)

    # epoch 1 (refresh shadow/fading sample)
    pm.set_epoch(1)
    pl1 = pm.calculate_path_loss(tx, rx, env)
    p1 = rx_power_dbm(tx.transceiver_properties.transmit_power_dbm, tx.transceiver_properties.antenna_gain_dbi, 0.0, pl1)

    print(f"RSRP epoch0={p0:.2f} dBm, epoch1={p1:.2f} dBm (should differ due to fading/shadowing)")

if __name__ == "__main__":
    main()
