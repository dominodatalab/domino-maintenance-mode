from typing import List
import aiohttp

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)
from domino_maintenance_mode.projects import Project


class Interface(ExecutionInterface[str]):
    def singular(self) -> str:
        return "Job"

    async def list_running(
        self, session: aiohttp.ClientSession, projects: List[Project]
    ) -> List[Execution[str]]:
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

    def is_restartable(self) -> bool:
        return False
