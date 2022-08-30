from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
    Project,
)


class Interface(ExecutionTypeInterface[str]):
    def singular(self) -> str:
        return "ImageBuild"

    def list_running(self, project_ids: List[Project]) -> List[Execution[str]]:
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
