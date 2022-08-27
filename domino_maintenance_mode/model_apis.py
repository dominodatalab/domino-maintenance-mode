from typing import List

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
)


class Interface(ExecutionTypeInterface):
    def singular(self) -> str:
        return "Model API"

    def list_running(self, project_ids: List[str]) -> List[Execution]:
        # TODO
        # Iterate Projects (self.project_ids)
        # GET /modelManager/getModels?projectId
        pass

    def stop(self, _id: str):
        # TODO
        # POST /v4/models/{modelId}/{modelVersionId}/stopModelDeployment
        pass

    def start(self, _id: str):
        # TODO
        # POST /v4/models/{modelId}/{modelVersionId}/startModelDeployment
        pass

    def is_stopped(self, _id: str) -> bool:
        # TODO
        # GET /v4/models/{modelId}/{modelVersionId}/getModelDeploymentStatus
        # status field
        pass

    def is_running(self, _id: str) -> bool:
        # TODO
        # GET /v4/models/{modelId}/{modelVersionId}/getModelDeploymentStatus
        # status field
        pass
