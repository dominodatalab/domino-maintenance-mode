from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
    Project,
)


class Interface(ExecutionTypeInterface[str]):
    def singular(self) -> str:
        return "Model API"

    def list_running(self, project_ids: List[Project]) -> List[Execution[str]]:
        # TODO
        # Iterate Projects (self.project_ids)
        # GET /modelManager/getModels?projectId
        return []

    def stop(self, _id: str):
        # TODO
        # POST /v4/models/{modelId}/{modelVersionId}/stopModelDeployment
        return

    def start(self, _id: str):
        # TODO
        # POST /v4/models/{modelId}/{modelVersionId}/startModelDeployment
        return

    def is_stopped(self, _id: str) -> bool:
        # TODO
        # GET /v4/models/{modelId}/{modelVersionId}/getModelDeploymentStatus
        # status field
        return True

    def is_running(self, _id: str) -> bool:
        # TODO
        # GET /v4/models/{modelId}/{modelVersionId}/getModelDeploymentStatus
        # status field
        return True
