from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
)


class Interface(ExecutionTypeInterface):
    def singular(self) -> str:
        return "Job"

    def list_running(self) -> List[Execution]:
        # TODO
        pass

    def stop(self, _id: str):
        # TODO
        pass

    def start(self, _id: str):
        # TODO
        pass

    def is_stopped(self, _id: str) -> bool:
        # TODO
        pass

    def is_running(self, _id: str) -> bool:
        # TODO
        pass
