import logging
from pprint import pformat
from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
    Project,
)

logger = logging.getLogger(__name__)

STOPPED_STATES = {"Stopped"}
RUNNING_STATES = {"Running"}


class Interface(ExecutionTypeInterface[str]):
    def singular(self) -> str:
        return "App"

    def list_running(self, projects: List[Project]) -> List[Execution[str]]:
        data = self.get("/v4/modelProducts")
        executions = []
        for app in data:
            logger.debug(pformat(app))
            try:
                if app["status"] in STOPPED_STATES:
                    continue
                executions.append(
                    Execution(
                        app["id"], app["name"], app["publisher"]["userName"]
                    )
                )
            except Exception as e:
                logger.warn(f"Error parsing App: '{pformat(app)}': {e}")
        return executions

    def stop(self, _id: str):
        self.post(f"/v4/modelProducts/{_id}/stop")

    def start(self, _id: str):
        self.post(f"/v4/modelProducts/{_id}/start")

    def is_stopped(self, _id: str) -> bool:
        data = self.get(f"/v4/modelProducts/{_id}")
        return data["status"] in STOPPED_STATES

    def is_running(self, _id: str) -> bool:
        data = self.get(f"/v4/modelProducts/{_id}")
        return data["status"] in RUNNING_STATES

    def is_restartable(self) -> bool:
        return True
