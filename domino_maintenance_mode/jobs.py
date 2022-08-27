from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
)


class Interface(ExecutionTypeInterface):
    def singular(self) -> str:
        return "Job"

    def list_running(self, project_ids: List[str]) -> List[Execution]:
        # TODO
        # Iterate Projects GET /projects/portfolio/getProjectPortfolio
        # GET /jobs?projectId
        pass

    def stop(self, _id: str):
        # TODO
        # POST /jobs/stop
        pass

    def start(self, _id: str):
        # TODO
        raise NotImplementedError("Relaunching Jobs is not implemented.")
        pass

    def is_stopped(self, _id: str) -> bool:
        # TODO
        # GET /jobs/{jobId}
        # statuses.executionStatus
        pass

    def is_running(self, _id: str) -> bool:
        # TODO
        # GET /jobs/{jobId}
        # statuses.executionStatus
        pass
