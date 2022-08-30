from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
    Project,
)


class Interface(ExecutionTypeInterface[str]):
    def singular(self) -> str:
        return "Job"

    def list_running(self, projects: List[Project]) -> List[Execution[str]]:
        # TODO
        # Iterate Projects GET /projects/portfolio/getProjectPortfolio
        # GET /jobs?projectId
        return []

    def stop(self, _id: str):
        # TODO
        # POST /jobs/stop
        return

    def start(self, _id: str):
        # TODO
        raise NotImplementedError("Relaunching Jobs is not implemented.")

    def is_stopped(self, _id: str) -> bool:
        # TODO
        # GET /jobs/{jobId}
        # statuses.executionStatus
        return True

    def is_running(self, _id: str) -> bool:
        # TODO
        # GET /jobs/{jobId}
        # statuses.executionStatus
        return True
