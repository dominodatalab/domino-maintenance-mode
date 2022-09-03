import logging
from dataclasses import dataclass
from typing import List

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)
from domino_maintenance_mode.projects import Project

# From ModelVersionStatus.scala
RUNNING_STATES = {"Running"}
STOPPED_STATES = {"Stopped", "Failed", "Ready to run"}
RUNNING_OR_LAUNCHING_STATES = {
    "Preparing to build",
    "Building",
    "Starting",
    "Running",
    "Stalled",
}

logger = logging.getLogger(__name__)


@dataclass
class ModelVersionId:
    _id: str
    modelId: str
    isActive: bool


class Interface(ExecutionInterface[ModelVersionId]):
    def id_from_value(self, v) -> ModelVersionId:
        return ModelVersionId(**v)

    def singular(self) -> str:
        return "Model API Version"

    def list_running(
        self, projects: List[Project]
    ) -> List[Execution[ModelVersionId]]:
        running_executions = []
        for project in projects:
            models = self.get(
                f"/v4/modelManager/getModels?projectId={project._id}"
            )
            for model in models:
                versions = []
                page = 1
                query = f"pageNumber={page}&pageSize=10"
                data = self.get(f"/models/{model['id']}/versions/json?{query}")
                while len(data["results"]) > 0:
                    versions.extend(data["results"])
                    page += 1
                    query = f"pageNumber={page}&pageSize=10"
                    data = self.get(
                        f"/models/{model['id']}/versions/json?{query}"
                    )
                for version in versions:
                    if (
                        version["deploymentStatus"]["name"]
                        in RUNNING_OR_LAUNCHING_STATES
                        or version["deploymentStatus"]["isPending"]
                    ):
                        running_executions.append(
                            Execution(
                                ModelVersionId(
                                    version["id"],
                                    model["id"],
                                    version["id"]
                                    == model["activeModelVersionId"],
                                ),
                                f"{model['name']} Version {version['number']}",
                                version["creator"]["name"],
                            )
                        )
        return running_executions

    def stop(self, _id: ModelVersionId):
        self.post(f"/v4/models/{_id.modelId}/{_id._id}/stopModelDeployment")

    def start(self, _id: ModelVersionId):
        if _id.isActive:
            self.post(
                f"/v4/models/{_id.modelId}/{_id._id}/startModelDeployment"
            )

    def is_stopped(self, _id: ModelVersionId) -> bool:
        version = self.get(f"/models/{_id.modelId}/versions/{_id._id}/json")[
            "result"
        ]
        return (
            version["deploymentStatus"]["name"] in STOPPED_STATES
            and not version["deploymentStatus"]["isPending"]
        )

    def is_running(self, _id: ModelVersionId) -> bool:
        if _id.isActive:
            version = self.get(
                f"/models/{_id.modelId}/versions/{_id._id}/json"
            )["result"]
            return version["deploymentStatus"]["name"] in RUNNING_STATES
        else:
            return True

    def is_restartable(self) -> bool:
        return True
