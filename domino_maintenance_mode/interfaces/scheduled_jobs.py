import logging
from dataclasses import dataclass
from typing import List
import aiohttp

from tqdm import tqdm  # type: ignore

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)
from domino_maintenance_mode.projects import Project

from domino_maintenance_mode.util import gather_with_concurrency

logger = logging.getLogger(__name__)


@dataclass
class ScheduledJobId:
    key: str
    projectId: str


class Interface(ExecutionInterface[ScheduledJobId]):
    concurrency: int

    def __init__(self, concurrency, **kwargs):
        self.concurrency = concurrency

    def id_from_value(self, v) -> ScheduledJobId:
        return ScheduledJobId(**v)

    def singular(self) -> str:
        return "Scheduled Job"

    async def list_running(
        self, session: aiohttp.ClientSession, projects: List[Project]
    ) -> List[Execution[ScheduledJobId]]:
        logger.info("Scanning Scheduled Jobs by Project")
        pbar = tqdm(total=len(projects), desc="Projects")
        ret = await gather_with_concurrency(
            self.concurrency,
            *[
                self.list_scheduled_jobs_by_project(session, project, pbar)
                for project in projects
            ],
        )

        return [item for sublist in ret for item in sublist]

    async def list_scheduled_jobs_by_project(
        self, session: aiohttp.ClientSession, project: Project, pbar
    ) -> List[Execution[ScheduledJobId]]:
        running_executions = []
        jobs = []

        try:
            jobs = await self.async_get(
                session, f"/v4/projects/{project._id}/scheduledjobs"
            )
        except Exception as e:
            logger.error(
                (
                    f"Exception while querying Scheduled Jobs "
                    f"for Project '{project._id}': {e}"
                )
            )
        for job in tqdm(jobs, desc="Scheduled Jobs"):
            try:
                if not job["isPaused"]:
                    running_executions.append(
                        Execution(
                            ScheduledJobId(job["id"], job["projectId"]),
                            job["title"],
                            job["scheduledByUserName"],
                        )
                    )
            except Exception as e:
                logger.error(
                    f"Error parsing Scheduled Job: {job.get('id')}: {e}"
                )

        pbar.update(1)

        return running_executions

    def __update_scheduled_job_is_paused(
        self, _id: ScheduledJobId, is_paused: bool
    ):
        job = self.get(f"/v4/projects/{_id.projectId}/scheduledjobs/{_id.key}")
        job["isPaused"] = is_paused
        self.put(
            f"/v4/projects/{_id.projectId}/scheduledjobs/{_id.key}",
            json=job,
        )

    def stop(self, _id: ScheduledJobId):
        self.__update_scheduled_job_is_paused(_id, True)

    def start(self, _id: ScheduledJobId):
        self.__update_scheduled_job_is_paused(_id, False)

    def is_stopped(self, _id: ScheduledJobId) -> bool:
        job = self.get(f"/v4/projects/{_id.projectId}/scheduledjobs/{_id.key}")
        return job["isPaused"]

    def is_running(self, _id: ScheduledJobId) -> bool:
        job = self.get(f"/v4/projects/{_id.projectId}/scheduledjobs/{_id.key}")
        return not job["isPaused"]

    def is_restartable(self) -> bool:
        return True
