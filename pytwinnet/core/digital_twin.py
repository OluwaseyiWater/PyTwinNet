
from __future__ import annotations
import copy
from dataclasses import dataclass, field
from typing import Optional
from .network import Network
from ..physics.environment import Environment
from ..physics.propagation import PropagationModel

@dataclass
class DigitalTwin:
    network: Network = field(default_factory=Network)
    environment: Optional[Environment] = None
    propagation_model: Optional[PropagationModel] = None
    def snapshot(self) -> "DigitalTwin":
        return copy.deepcopy(self)
    def set_environment(self, env: Environment) -> None:
        self.environment = env
    def set_propagation_model(self, model: PropagationModel) -> None:
        self.propagation_model = model
