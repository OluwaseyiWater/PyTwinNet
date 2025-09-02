import numpy as np
from pytwinnet import DigitalTwin, Network, WirelessNode, TransceiverProperties
from pytwinnet.physics import Environment, FreeSpacePathLoss
from pytwinnet.accelerate import fspl_matrix_db, rsrp_matrix_dbm, max_rsrp_association_vectorized

def main():
    twin = DigitalTwin()
    twin.set_environment(Environment(dimensions_m=(1000, 1000, 30)))
    twin.set_propagation_model(FreeSpacePathLoss())

    net = Network()
    # 10 gNBs
    for i in range(10):
        net.add_node(WirelessNode(
            node_id=f"gNB-{i+1}",
            position=(100 + 80*i, 100 + 30*i, 10.0),
            transceiver_properties=TransceiverProperties(transmit_power_dbm=32.0, antenna_gain_dbi=5.0),
            metadata={"role": "gNB"},
        ))
    # 200 UEs on a grid
    for r in range(20):
        for c in range(10):
            idx = r*10 + c + 1
            net.add_node(WirelessNode(node_id=f"UE-{idx}", position=(20 + 45*c, 20 + 40*r, 1.5)))
    twin.network = net

    tx_ids = [f"gNB-{i+1}" for i in range(10)]
    ue_ids = [f"UE-{i+1}" for i in range(200)]

    assoc = max_rsrp_association_vectorized(twin, tx_ids, ue_ids)
    # Show first 10 associations
    print({k: assoc[k] for k in list(assoc)[:10]})

if __name__ == "__main__":
    main()
