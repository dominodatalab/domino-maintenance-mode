import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

import requests

logger = logging.getLogger(__name__)

Id = TypeVar("Id")


@dataclass
class Execution(Generic[Id]):
    _id: Id
    name: str
    owner: str


@dataclass
class Project:
    _id: str
    name: str
    owner: str


class ExecutionTypeInterface(ABC, Generic[Id]):
    def __init__(self):
        api_key = os.environ["DOMINO_API_KEY"]
        self.hostname = os.environ["DOMINO_HOSTNAME"]
        # TODO: Ability to trust custom certs?
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "X-Domino-Api-Key": api_key,
            }
        )

    def get(self, path: str, success_code: int = 200) -> dict:
        response = self.session.get(f"{self.hostname}{path}")
        if response.status_code != success_code:
            raise Exception(
                f"API returned error ({response.status_code}): {response.text}"
            )
        return response.json()

    def post(
        self, path: str, json: Optional[dict] = None, success_code: int = 200
    ) -> dict:
        response = self.session.post(f"{self.hostname}{path}", json=json)
        if response.status_code != success_code:
            raise Exception(
                f"API returned error ({response.status_code}): {response.text}"
            )
        return response.json()

    @abstractmethod
    def singular(self) -> str:
        pass

    @abstractmethod
    def list_running(self, projects: List[Project]) -> List[Execution[Id]]:
        """List non-stopped (running or pending) executions."""
        pass

    @abstractmethod
    def stop(self, _id: Id):
        """Initiate shutdown of an execution. Throws exception on failure."""
        pass

    @abstractmethod
    def start(self, _id: Id):
        """Initiate launch of an execution. Throws exception on failure."""
        pass

    @abstractmethod
    def is_running(self, _id: Id) -> bool:
        """Is the execution in a stopped state."""
        pass

    @abstractmethod
    def is_stopped(self, _id: Id) -> bool:
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
        batch_size: int = 5,
        batch_interval_s: int = 30,
        max_failures: int = 5,
        grace_period_s: int = 600,
    ):
        self.batch_size = batch_size
        self.batch_interval_s = batch_interval_s
        self.grace_period_s = grace_period_s
        self.max_failures = max_failures
        self.projects = self.__fetch_projects()
        logger.info(f"Initialized, found {len(self.projects)} projects.")

    def __fetch_projects(self) -> List[Project]:
        api_key = os.environ["DOMINO_API_KEY"]
        hostname = os.environ["DOMINO_HOSTNAME"]

        data = requests.get(
            f"{hostname}/v4/projects",
            headers={
                "Content-Type": "application/json",
                "X-Domino-Api-Key": api_key,
            },
        ).json()
        return list(
            map(
                lambda project: Project(
                    project["id"], project["name"], project["ownerUsername"]
                ),
                data,
            )
        )

    def shutdown(self, interface: ExecutionTypeInterface):
        self.interface = interface
        self.typ = interface.singular()

        logger.info(f"Shutting down {self.typ}s")

        running_executions = self.interface.list_running(self.projects)
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
            self.__batch_stop()
            self.__wait()

        logger.info(f"{self.typ}s successfully shut down.")

    def __batch_stop(self):
        while len(self.executions) > 0:
            batch = [
                self.executions.pop()
                for _ in range(min(len(self.executions), self.batch_size))
            ]

            for execution in batch:
                self.__stop_execution(execution)

            if len(self.executions) > 0:
                logger.info(
                    f"Batch complete, {len(self.executions)} remaining."
                )
                time.sleep(self.batch_interval_s)

    def __stop_execution(self, execution: Execution):
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

    def __wait(self):
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
