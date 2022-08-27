import logging
import time
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
    batch_size: int
    batch_interval_s: int
    max_failures: int
    grace_period_s: int
    failures: dict = dict()

    def __init__(
        self,
        typ: str,
        interface: ExecutionTypeInterface,
        batch_size: int = 5,
        batch_interval_s: int = 30,
        max_failures: int = 5,
        grace_period_s: int = 600,
    ):
        self.interface = interface
        self.typ = typ
        self.batch_size = batch_size
        self.batch_interval_s = batch_interval_s
        self.grace_period_s = grace_period_s
        self.max_failures = max_failures

    def shutdown(self):
        logger.info(f"Shutting down {self.typ}s")

        running_executions = self.interface.list_running()
        logger.debug(running_executions)
        logger.info(f"Found {len(running_executions)} running {self.typ}(s)")

        if len(running_executions) > 0:
            if input(
                "Are you sure you want to shut down these executions? "
            ).lower() not in {"y", "yes"}:
                return

            self.executions = running_executions
            self.failed = []
            self.stopping = []
            self.batch_stop()
            self.wait()

        logger.info(f"{self.typ}s successfully shut down.")

    def batch_stop(self):
        while len(self.executions) > 0:
            batch = [
                self.executions.pop()
                for _ in range(min(len(self.executions), self.batch_size))
            ]

            for execution in batch:
                self.stop_execution(execution)

            if len(self.executions) > 0:
                logger.info(
                    f"Batch complete, {len(self.executions)} remaining."
                )
                time.sleep(self.batch_interval_s)

    def stop_execution(self, execution: Execution):
        try:
            self.interface.stop(execution._id)
            logger.info(f"Stopped {self.typ} '{execution.name}'")
            self.stopping.append(execution)
        except Exception as e:
            self.failures[execution._id] = (
                self.failures.get(execution._id, 0) + 1
            )
            if self.failures[execution._id] < self.max_failures:
                logger.warn(
                    f"Error stopping {self.typ} '{execution.name}': {e}"
                )
                self.executions.insert(0, execution)
            else:
                logger.warn(
                    f"Failed to stop {self.typ} '{execution.name}': {e}"
                )
                self.failed.append(execution)

    def wait(self):
        logger.info(
            f"Waiting up to {self.grace_period_s}s for {self.typ}s to stop."
        )
        tic = time.time()
        while len(self.stopping) > 0:
            if (time.time() - tic) >= self.grace_period_s:
                raise TimeoutError()
            execution = self.stopping.pop()
            try:
                stopped = self.interface.is_stopped(execution._id)
            except Exception as e:
                logger.warn(f"Error polling {self.typ} state: {e}")
                stopped = False

            if stopped:
                logger.info(f"{self.typ} '{execution.name}' has stopped.")
            else:
                self.stopping.insert(0, execution)
            time.sleep(1)
