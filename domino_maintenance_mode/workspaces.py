from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
)


class Interface(ExecutionTypeInterface):
    def singular(self) -> str:
        return "Workspace"

    def list_running(self, project_ids: List[str]) -> List[Execution]:
        # TODO
        # Iterate Projects GET /projects/portfolio/getProjectPortfolio
        # GET /workspaces?projectId
        pass

    def stop(self, _id: str):
        # TODO
        # POST /workspaces/stop/end
        pass

    def start(self, _id: str):
        raise NotImplementedError("Relaunching Workspaces is not implemented.")

    def is_stopped(self, _id: str) -> bool:
        # TODO
        # GET /workspaces/workspace/{workspaceId}
        # Check status field
        pass

    def is_running(self, _id: str) -> bool:
        # TODO
        # GET /workspaces/workspace/{workspaceId}
        # Check status field
        pass
