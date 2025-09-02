# PyTwinNet

Wireless **Digital Twin** & **Network Optimization** library for research and prototyping.

## Install

```bash
pip install pytwinnet                 # core
pip install pytwinnet[accel,cli]      # with Numba + CLI
pip install pytwinnet[all]            # everything (dev/docs too)


## Quickstart

import pytwinnet as ptn
from pytwinnet.physics import Environment, FreeSpacePathLoss

twin = ptn.DigitalTwin()
twin.set_environment(Environment(dimensions_m=(300,300,30)))
twin.set_propagation_model(FreeSpacePathLoss())



### `LICENSE`
Use MIT (or your preferred). MIT example is fine.

## Step 3: Ensure `__version__` is exposed

In `pytwinnet/__init__.py`:

```python
__version__ = "0.1.0"

from .core.digital_twin import DigitalTwin
from .core.network import Network
from .core.node import WirelessNode, TransceiverProperties

