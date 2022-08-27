from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
)


class Interface(ExecutionTypeInterface):
    def singular(self) -> str:
        return "Scheduled Job"

    def list_running(self, project_ids: List[str]) -> List[Execution]:
        # TODO
        # Iterate Projects GET /projects/portfolio/getProjectPortfolio
        # GET /projects/{projectId}/scheduledjobs
        pass

    def stop(self, _id: str):
        # TODO
        # PUT /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # Set isPaused true
        pass

    def start(self, _id: str):
        # TODO
        # PUT /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # Set isPaused false
        pass

    def is_stopped(self, _id: str) -> bool:
        # TODO
        # GET /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # isPaused == true
        pass

    def is_running(self, _id: str) -> bool:
        # TODO
        # GET /projects/{projectId}/scheduledjobs/{scheduledJobKey}
        # isPaused == false
        pass
