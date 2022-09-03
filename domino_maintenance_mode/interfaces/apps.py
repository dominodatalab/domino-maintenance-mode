import logging
from dataclasses import asdict, dataclass
from pprint import pformat
from typing import List

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)
from domino_maintenance_mode.projects import Project

logger = logging.getLogger(__name__)

STOPPED_STATES = {"Stopped"}
RUNNING_STATES = {"Running"}


@dataclass
class StartRequest:
    hardwareTierId: str
    externalVolumeMountIds: List[str]


@dataclass
class AppId:
    _id: str
    hardwareTierId: str
    projectId: str


class Interface(ExecutionInterface[AppId]):
    def id_from_value(self, v) -> AppId:
        return AppId(**v)

    def singular(self) -> str:
        return "App"

    def list_running(self, projects: List[Project]) -> List[Execution[AppId]]:
        data = self.get("/v4/modelProducts")
        logger.info(pformat(data))
        executions = []
        for app in data:
            logger.debug(pformat(app))
            try:
                if app["status"] in STOPPED_STATES:
                    continue
                executions.append(
                    Execution(
                        AppId(
                            app["id"], app["hardwareTierId"], app["projectId"]
                        ),
                        app["name"],
                        app["publisher"]["userName"],
                    )
                )
            except Exception as e:
                logger.warn(f"Error parsing App: '{pformat(app)}': {e}")
        return executions

    def stop(self, _id: AppId):
        self.post(f"/v4/modelProducts/{_id._id}/stop")

    def start(self, _id: AppId):
        # List EDVs
        edvIds = list(
            map(
                lambda edv: edv["id"],
                filter(
                    lambda edv: any(
                        map(
                            lambda dataPlane: dataPlane["isLocal"],
                            edv["dataPlanes"],
                        )
                    ),
                    self.get(f"/v4/datamount/projects/{_id.projectId}"),
                ),
            )
        )
        self.post(
            f"/v4/modelProducts/{_id._id}/start",
            json=asdict(
                StartRequest(
                    _id.hardwareTierId,
                    edvIds,
                )
            ),
        )

    def is_stopped(self, _id: AppId) -> bool:
        data = self.get(f"/v4/modelProducts/{_id._id}")
        return data["status"] in STOPPED_STATES

    def is_running(self, _id: AppId) -> bool:
        data = self.get(f"/v4/modelProducts/{_id._id}")
        return data["status"] in RUNNING_STATES

    def is_restartable(self) -> bool:
        return True
