import logging
from dataclasses import dataclass
from typing import Any, Dict, List
import aiohttp

from tqdm import tqdm  # type: ignore

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)
from domino_maintenance_mode.projects import Project

# From WorkspaceState.scala
RUNNING_OR_LAUNCHING_STATES = {
    "Created",
    "Initializing",
    "Starting",
    "Started",
}
BASE_PATH: str = "/v4/workspace"

logger = logging.getLogger(__name__)


@dataclass
class WorkspaceId:
    _id: str
    projectId: str


class Interface(ExecutionInterface[WorkspaceId]):
    page_size: int

    def __init__(self, workspaces_page_size, **kwargs):
        self.page_size = workspaces_page_size

    def id_from_value(self, v) -> WorkspaceId:
        return WorkspaceId(**v)

    def singular(self) -> str:
        return "Workspace"

    async def list_running(
        self, session: aiohttp.ClientSession, projects: List[Project]
    ) -> List[Execution[WorkspaceId]]:
        logger.info(f"Scanning Workspaces. Page size: {self.page_size}")

        project_lookup = {
            (project.owner, project.name): project._id for project in projects
        }

        offset = 0
        workspaces: Dict[str, Any] = {}
        try:
            while True:
                params = f"limit={self.page_size}&offset={offset}"
                data = self.get(f"{BASE_PATH}/adminDashboardRowData?{params}")
                last_count = len(workspaces)
                for entry in data.get("tableRows", []):
                    project_id = project_lookup[
                        (entry["projectOwnerName"], entry["projectName"])
                    ]
                    entry["projectId"] = project_id
                    workspaces[entry["workspaceId"]] = entry
                logger.debug(
                    (
                        f"Got {len(data.get('tableRows', []))}"
                        f" entries, {len(workspaces) - last_count} new,"
                        f" offset: {offset},"
                        f" limit: {self.page_size}"
                    )
                )
                if len(workspaces) >= data["totalEntries"]:
                    break
                offset += 1
                # If the list of workspaces has changed, loop again
                if offset * self.page_size >= data["totalEntries"]:
                    raise Exception(
                        (
                            "Number of Workspaces found did not match"
                            " 'totalEntries':"
                            f" {len(workspaces)}/{data['totalEntries']}"
                        )
                    )
        except Exception as e:
            logger.error(
                (
                    f"Error querying Workspaces: {e}, snapshot may "
                    "not include all Workspaces."
                )
            )

        running_executions = []
        for workspace in tqdm(
            workspaces.values(), desc="Workspaces", total=len(workspaces)
        ):
            try:
                if workspace["workspaceState"] in RUNNING_OR_LAUNCHING_STATES:
                    running_executions.append(
                        Execution(
                            WorkspaceId(
                                workspace["workspaceId"],
                                workspace["projectId"],
                            ),
                            f"{workspace['projectName']}/{workspace['name']}",
                            f"{workspace['ownerUsername']}",
                        )
                    )
            except Exception as e:
                logger.error(
                    (
                        f"Error parsing Workspace "
                        f"{workspace.get('workspaceId')}: {e}"
                    )
                )
        return running_executions

    def stop(self, _id: WorkspaceId):
        self.post(
            f"{BASE_PATH}/project/{_id.projectId}/workspace/{_id._id}/stop"
        )

    def start(self, _id: WorkspaceId):
        raise NotImplementedError("Relaunching Workspaces is not implemented.")

    def is_stopped(self, _id: WorkspaceId) -> bool:
        workspace = self.get(
            f"{BASE_PATH}/project/{_id.projectId}/workspace/{_id._id}"
        )
        return workspace["mostRecentSession"]["sessionStatusInfo"][
            "isCompleted"
        ]

    def is_running(self, _id: WorkspaceId) -> bool:
        workspace = self.get(
            f"{BASE_PATH}/project/{_id.projectId}/workspace/{_id._id}"
        )
        return workspace["mostRecentSession"]["sessionStatusInfo"]["isRunning"]

    def is_restartable(self) -> bool:
        return False
