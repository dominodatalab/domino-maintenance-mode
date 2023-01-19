from typing import List

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)
from domino_maintenance_mode.projects import Project


class Interface(ExecutionInterface[str]):
    def singular(self) -> str:
        return "ImageBuild"

    async def list_running(self, projects: List[Project]) -> List[Execution[str]]:
        # TODO
        return []

    def stop(self, _id: str):
        # TODO
        return

    def start(self, _id: str):
        # TODO
        raise NotImplementedError(
            "Relaunching ImageBuilds is not implemented."
        )

    def is_stopped(self, _id: str) -> bool:
        # TODO
        return True

    def is_running(self, _id: str) -> bool:
        # TODO
        return True

    def is_restartable(self) -> bool:
        return False
