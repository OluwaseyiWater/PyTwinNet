# Getting Started

## Installation
```bash
pip install pytwinnet
# or with extras:
pip install "pytwinnet[accel,cli]"

```python
import pytwinnet as ptn
from pytwinnet.physics import Environment, FreeSpacePathLoss

twin = ptn.DigitalTwin()
twin.set_environment(Environment(dimensions_m=(300,300,30)))
twin.set_propagation_model(FreeSpacePathLoss())

```bash
pytwinnet run configs/het_net_placement.yaml




