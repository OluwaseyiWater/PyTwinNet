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
# -> report.json + heatmap.png


## `docs/user_guide/overview.md`
```markdown
# User Guide Overview

- **DigitalTwin** orchestrates `Network`, `Environment`, `PropagationModel`.
- **Network / WirelessNode**: topology & radio properties.
- **Environment**: space, obstacles (future).
- **PropagationModel**: FSPL, shadowing/fading, RIS (stubs), vectorized fast paths.
- **Simulation/Scenarios**: move nodes, set power, RIS beam.
- **Optimization**: placement, grid/random, greedy, BayesOpt, GA, Pareto.

