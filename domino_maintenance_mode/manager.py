import datetime
import json
import logging
import time
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Dict, List, Optional

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)

logger = logging.getLogger(__name__)


@dataclass
class BatchCallResult:
    failed: List[Execution]
    success: List[Execution]


class Manager:
    batch_size: int
    batch_interval_s: int
    max_failures: int
    grace_period_s: int
    failures: dict = dict()

    def __init__(
        self,
        batch_size: int = 5,
        batch_interval_s: int = 5,
        max_failures: int = 5,
        grace_period_s: int = 600,
    ):
        self.batch_size = batch_size
        self.batch_interval_s = batch_interval_s
        self.grace_period_s = grace_period_s
        self.max_failures = max_failures

    def stop(self, interface: ExecutionInterface, executions: List[Execution]):
        self.__toggle_executions(
            "stop",
            interface.singular(),
            interface.stop,
            interface.is_stopped,
            executions,
        )

    def start(
        self, interface: ExecutionInterface, executions: List[Execution]
    ):
        self.__toggle_executions(
            "start",
            interface.singular(),
            interface.start,
            interface.is_running,
            executions,
        )

    def __persist_failed(
        self,
        verb: str,
        singular: str,
        session: str,
        action: List[Execution],
        wait: Optional[List[Execution]] = None,
    ):
        path = f"{session}-failed.json"
        if (wait is None and len(action) > 0) or (
            wait is not None and len(wait) > 0
        ):
            if wait is None:
                logger.error(
                    (
                        f"{len(action)} {singular}s failed to {verb}!"
                        f" Saving log to '{path}'."
                    )
                )
            else:
                logger.error(
                    (
                        f"{len(wait)} {singular}s timed out!"
                        " Updating log at '{path}'."
                    )
                )
            data = {
                "modify": list(map(asdict, action)),
                "timeout": list(map(asdict, wait))
                if wait is not None
                else None,
            }
            with open(path, "w") as f:
                json.dump(data, f)

    def __toggle_executions(
        self,
        verb: str,
        singular: str,
        toggle_func,
        wait_func,
        executions: List[Execution],
    ):
        if input(
            (
                f"Are you sure you want to {verb} these"
                f" {len(executions)} {singular}s? "
            )
        ).lower() not in {"y", "yes"}:
            return
        session = f"{singular}-{verb}-{datetime.datetime.now().isoformat()}"
        result = self.__batch_call(verb, singular, toggle_func, executions)
        self.__persist_failed(verb, singular, session, result.failed)
        wait_failed = self.__wait_condition(
            verb, singular, wait_func, result.success
        )
        self.__persist_failed(
            verb, singular, session, result.failed, wait_failed
        )

    def __batch_call(
        self, verb: str, singular: str, func, executions: List[Execution]
    ) -> BatchCallResult:
        """Batches / rate limits API calls to change execution state."""
        success: List[Execution] = []
        failed: List[Execution] = []
        failures: Dict[Any, int] = {}
        while len(executions) > 0:
            batch = [
                executions.pop()
                for _ in range(min(len(executions), self.batch_size))
            ]

            for execution in batch:
                try:
                    func(execution._id)
                    success.append(execution)
                    logger.info(
                        (
                            f"Successful {verb} of {singular}"
                            f" '{execution.name}'"
                        )
                    )
                except Exception as e:
                    if is_dataclass(execution._id):
                        key = execution._id._id
                    else:
                        key = execution._id
                    failures[key] = failures.get(key, 0) + 1
                    if failures[key] < self.max_failures:
                        logger.warn(
                            (
                                f"Failed to {verb} {singular} "
                                f"'{execution.name}' (retrying): {e}"
                            )
                        )
                        executions.insert(0, execution)
                    else:
                        logger.warn(
                            (
                                f"Failed to {verb} {singular} "
                                f"'{execution.name}': {e}"
                            )
                        )
                        failed.append(execution)

            if len(executions) > 0:
                logger.info(f"Batch complete, {len(executions)} remaining.")
                time.sleep(self.batch_interval_s)
        return BatchCallResult(failed, success)

    def __wait_condition(
        self, verb, singular, func, executions: List[Execution]
    ) -> List[Execution]:
        """Wait until `func` returns true for all executions in `self.waiting`

        Up to `self.grace_period_s`.
        """
        failed = [execution for execution in executions]
        logger.info(
            f"Waiting up to {self.grace_period_s}s for {singular}s to {verb}."
        )
        tic = time.time()
        while len(failed) > 0:
            if (time.time() - tic) >= self.grace_period_s:
                return failed
            execution = failed.pop()
            try:
                ready = func(execution._id)
            except Exception as e:
                logger.warn(f"Error polling {singular} state: {e}")
                ready = False

            if ready:
                logger.info(
                    f"Successful {verb} of {singular} '{execution.name}'."
                )
            else:
                failed.insert(0, execution)
            time.sleep(1)
        return failed
