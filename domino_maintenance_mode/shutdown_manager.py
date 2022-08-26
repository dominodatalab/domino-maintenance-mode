import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class Execution:
    _id: str
    name: str
    owner: str


class ExecutionTypeInterface(ABC):
    @abstractmethod
    def list_running(self) -> List[Execution]:
        """List non-stopped (running or pending) executions."""
        pass

    @abstractmethod
    def stop(self, _id: str):
        """Initiate shutdown of an execution. Throws exception on failure."""
        pass

    @abstractmethod
    def start(self, _id: str):
        """Initiate launch of an execution. Throws exception on failure."""
        pass

    @abstractmethod
    def is_running(self, _id: str) -> bool:
        """Is the execution in a stopped state."""
        pass

    @abstractmethod
    def is_stopped(self, _id: str) -> bool:
        """Is the execution fully running."""
        pass


class ShutdownManager:
    batch_size: int = 5

    def __init__(self, interface: ExecutionTypeInterface):
        self.interface = interface

    def shutdown(self):
        pass
