from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.scheduling import max_rsrp_association, proportional_fair_allocation

def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(300, 300, 30)))
    twin.set_propagation_model(FreeSpacePathLoss())

    net = Network()
    net.add_node(WirelessNode("gNB-1", position=(50, 50, 10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                              metadata={"role": "gNB"}))
    net.add_node(WirelessNode("gNB-2", position=(250, 250, 10),
                              transceiver_properties=TransceiverProperties(transmit_power_dbm=32, antenna_gain_dbi=5),
                              metadata={"role": "gNB"}))
    for i, pos in enumerate([(60,60,1.5),(80,80,1.5),(120,120,1.5),(200,210,1.5),(240,240,1.5),(260,260,1.5)]):
        net.add_node(WirelessNode(f"UE-{i+1}", position=pos))
    twin.network = net

    tx_ids = ["gNB-1", "gNB-2"]
    ue_ids = [f"UE-{i+1}" for i in range(6)]
    assoc = max_rsrp_association(twin, tx_ids, ue_ids)
    print("Association (UE -> TX):", assoc)

    sched = proportional_fair_allocation(twin, assoc, rb_count=20)
    for tx, ues in sched.items():
        print(f"{tx}: scheduled RBs ->", ues[:10], "...")

if __name__ == "__main__":
    main()
