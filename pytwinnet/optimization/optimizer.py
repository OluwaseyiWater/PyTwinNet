
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..core.digital_twin import DigitalTwin
from .objective import Objective

class Optimizer(ABC):
    @abstractmethod
    def optimize(self, twin: DigitalTwin, objective: Objective) -> Dict[str, Any]:
        raise NotImplementedError
