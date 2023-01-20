import logging
from dataclasses import dataclass
from typing import List
import aiohttp

from domino_maintenance_mode.util import (
    gather_with_concurrency
)

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
    concurrency: int

    def __init__(self, models_page_size, concurrency, **kwargs):
        self.page_size = models_page_size
        self.concurrency = concurrency

    def id_from_value(self, v) -> ModelVersionId:
        return ModelVersionId(**v)

    def singular(self) -> str:
        return "Model API Version"

    async def list_running(self, session: aiohttp.ClientSession, projects: List[Project]) -> List[Execution[ModelVersionId]]:
        logger.info("Scanning Models by Project")
        pbar = tqdm(total=len(projects), desc="Projects")
        ret = await gather_with_concurrency(self.concurrency, *[self.list_models_by_project(session, project, pbar) for project in projects])

        return [item for sublist in ret for item in sublist]
    
    async def list_models_by_project(self, session: aiohttp.ClientSession, project: Project, pbar) -> List[Execution[ModelVersionId]]:
        running_executions = [] 
        models = []

        try:
            models = await self.async_get(session, 
                        f"/v4/modelManager/getModels?projectId={project._id}"
                    )
        except Exception as e:
            logger.error(
                (
                    f"Exception while querying models for "
                    f"project '{project._id}': {e}"
                )
            )

        for model in tqdm(models, desc="Models"):
            try:
                versions = []
                page = 1
                query = f"pageNumber={page}&pageSize={self.page_size}"
                data = await self.async_get(session,
                    f"/models/{model['id']}/versions/json?{query}"
                )
                while len(data["results"]) > 0:
                    versions.extend(data["results"])
                    page += 1
                    query = f"pageNumber={page}&pageSize={self.page_size}"
                    data = await self.async_get(session,
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

        pbar.update(1)

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
