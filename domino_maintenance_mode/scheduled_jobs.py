from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
    Project,
)


class Interface(ExecutionTypeInterface[str]):
    def singular(self) -> str:
        return "Scheduled Job"

    def list_running(self, project_ids: List[Project]) -> List[Execution[str]]:
        # TODO
        # Iterate Projects GET /projects/portfolio/getProjectPortfolio
        # GET /projects/{projectId}/scheduledjobs
        return []

    def stop(self, _id: str):
        # TODO
        # PUT /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # Set isPaused true
        return

    def start(self, _id: str):
        # TODO
        # PUT /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # Set isPaused false
        return

    def is_stopped(self, _id: str) -> bool:
        # TODO
        # GET /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # isPaused == true
        return True

    def is_running(self, _id: str) -> bool:
        # TODO
        # GET /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # isPaused == false
        return True
