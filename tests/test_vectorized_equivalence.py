import numpy as np
from pytwinnet.physics import FreeSpacePathLoss
from pytwinnet.accelerate.vectorized import fspl_matrix_db
from pytwinnet.core.node import WirelessNode, TransceiverProperties   # ← add TransceiverProperties
from pytwinnet.physics.environment import Environment

def test_fspl_vector_matches_scalar():
    pm = FreeSpacePathLoss()
    rng = np.random.default_rng(0)
    tx_xyz = rng.uniform(0, 300, size=(5,3))
    rx_xyz = rng.uniform(0, 300, size=(7,3))
    f = 3.5e9
    m = fspl_matrix_db(tx_xyz, rx_xyz, f)
    env = Environment(dimensions_m=(300,300,30))

    for i in range(5):
        for j in range(7):
            # Ensure the TX node uses the SAME carrier frequency as the vectorized call
            tx = WirelessNode(
                "t",
                position=tuple(tx_xyz[i]),
                transceiver_properties=TransceiverProperties(carrier_frequency_hz=f),
            )
            rx = WirelessNode("r", position=tuple(rx_xyz[j]))
            s = pm.calculate_path_loss(tx, rx, env)
            assert abs(s - m[i, j]) < 1e-5
