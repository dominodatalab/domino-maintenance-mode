from dataclasses import dataclass
from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
    Project,
)

# From WorkspaceState.scala
RUNNING_STATES = {"Started"}
STOPPED_STATES = {"Stopped", "Deleted"}
RUNNING_OR_LAUNCHING_STATES = {
    "Created",
    "Initializing",
    "Starting",
    "Started",
}
BASE_PATH: str = "/v4/workspace"


@dataclass
class WorkspaceId:
    _id: str
    projectId: str


class Interface(ExecutionTypeInterface[WorkspaceId]):
    def singular(self) -> str:
        return "Workspace"

    def list_running(
        self, projects: List[Project]
    ) -> List[Execution[WorkspaceId]]:
        project_lookup = {
            (project.owner, project.name): project._id for project in projects
        }

        offset = 1000
        limit = 50
        workspaces = {}
        while True:
            params = f"limit={limit}&offset={offset}"
            data = self.get(f"{BASE_PATH}/adminDashboardRowData?{params}")
            for entry in data.get("tableRows", []):
                project_id = project_lookup[
                    (entry["projectOwnerName"], entry["projectName"])
                ]
                entry["projectId"] = project_id
                workspaces[entry["workspaceId"]] = entry
            if len(workspaces) >= data["totalEntries"]:
                break
            offset += 1
            # If the list of workspaces has changed, loop again
            if offset * limit >= data["totalEntries"]:
                offset = 0

        running_executions = []
        for workspace in workspaces.values():
            if workspace["workspaceState"] in RUNNING_OR_LAUNCHING_STATES:
                running_executions.append(
                    Execution(
                        WorkspaceId(
                            workspace["workspaceId"], workspace["projectId"]
                        ),
                        f"{workspace['projectName']}/{workspace['name']}",
                        f"{workspace['ownerUsername']}",
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
        return workspace["state"] in STOPPED_STATES

    def is_running(self, _id: WorkspaceId) -> bool:
        workspace = self.get(
            f"{BASE_PATH}/project/{_id.projectId}/workspace/{_id._id}"
        )
        return workspace["state"] in RUNNING_STATES
