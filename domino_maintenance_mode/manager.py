import logging
import time
from typing import List

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)

logger = logging.getLogger(__name__)


class ShutdownManager:
    batch_size: int
    batch_interval_s: int
    max_failures: int
    grace_period_s: int
    failures: dict = dict()

    def __init__(
        self,
        batch_size: int = 5,
        batch_interval_s: int = 30,
        max_failures: int = 5,
        grace_period_s: int = 600,
    ):
        self.batch_size = batch_size
        self.batch_interval_s = batch_interval_s
        self.grace_period_s = grace_period_s
        self.max_failures = max_failures

    def shutdown(self, interface: ExecutionInterface, state: dict):
        self.interface = interface
        self.typ = interface.singular()

        logger.info(f"Shutting down {self.typ}s")

        running_executions = state[interface.singular()]
        logger.debug(running_executions)
        logger.info(f"Found {len(running_executions)} running {self.typ}(s)")
        if len(running_executions) > 0:
            if input(
                "Are you sure you want to shut down these executions? "
            ).lower() not in {"y", "yes"}:
                return

            self.executions = running_executions
            self.failed: List[Execution] = []
            self.stopping: List[Execution] = []
            self.__batch_toggle(self.interface.stop)
            self.__wait_condition(self.interface.is_stopped)

        logger.info(f"{self.typ}s successfully shut down.")

    def __batch_toggle(self, func):
        while len(self.executions) > 0:
            batch = [
                self.executions.pop()
                for _ in range(min(len(self.executions), self.batch_size))
            ]

            for execution in batch:
                self.__toggle_execution(execution, func)

            if len(self.executions) > 0:
                logger.info(
                    f"Batch complete, {len(self.executions)} remaining."
                )
                time.sleep(self.batch_interval_s)

    def __toggle_execution(self, execution: Execution, func):
        try:
            func(execution._id)
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

    def __wait_condition(self, func):
        logger.info(
            f"Waiting up to {self.grace_period_s}s for {self.typ}s to stop."
        )
        tic = time.time()
        while len(self.stopping) > 0:
            if (time.time() - tic) >= self.grace_period_s:
                raise TimeoutError()
            execution = self.stopping.pop()
            try:
                stopped = func(execution._id)
            except Exception as e:
                logger.warn(f"Error polling {self.typ} state: {e}")
                stopped = False

            if stopped:
                logger.info(f"{self.typ} '{execution.name}' has stopped.")
            else:
                self.stopping.insert(0, execution)
            time.sleep(1)
