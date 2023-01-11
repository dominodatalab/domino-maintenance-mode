import logging
from dataclasses import dataclass
from typing import List

from tqdm import tqdm  # type: ignore

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
    page_size: int

    def __init__(
        self,
        models_page_size,
        **kwargs
    ):
        self.page_size = models_page_size

    def id_from_value(self, v) -> ModelVersionId:
        return ModelVersionId(**v)

    def singular(self) -> str:
        return "Model API Version"

    def list_running(
        self, projects: List[Project]
    ) -> List[Execution[ModelVersionId]]:
        logger.info(F"Scanning Model API Versions by Project. Page size: {self.page_size}")
        running_executions = []
        for project in tqdm(projects, desc="Projects"):
            try:
                models = self.get(
                    f"/v4/modelManager/getModels?projectId={project._id}"
                )
            except Exception as e:
                logger.error(
                    (
                        f"Exception while querying models for "
                        f"project '{project._id}': {e}"
                    )
                )
                continue
            for model in tqdm(models, desc="Models"):
                try:
                    versions = []
                    page = 1
                    query = f"pageNumber={page}&pageSize={self.page_size}"
                    data = self.get(
                        f"/models/{model['id']}/versions/json?{query}"
                    )
                    while len(data["results"]) > 0:
                        versions.extend(data["results"])
                        page += 1
                        query = f"pageNumber={page}&pageSize={self.page_size}"
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
                                    f"{model['name']} #{version['number']}",
                                    version["creator"]["name"],
                                )
                            )
                except Exception as e:
                    logger.error(
                        (
                            f"Exception while detecting state of "
                            f"Model API {model.get('id')}: {e}"
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
