
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable

class DataSource(ABC):
    @abstractmethod
    def connect(self) -> None: ...
    @abstractmethod
    def read_data(self) -> Iterable[object]:
        raise NotImplementedError
