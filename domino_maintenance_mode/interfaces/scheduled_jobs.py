from dataclasses import dataclass
from typing import List

from domino_maintenance_mode.execution_interface import (
    Execution,
    ExecutionInterface,
)
from domino_maintenance_mode.projects import Project


@dataclass
class ScheduledJobId:
    key: str
    projectId: str


class Interface(ExecutionInterface[ScheduledJobId]):
    def id_from_value(self, v) -> ScheduledJobId:
        return ScheduledJobId(**v)

    def singular(self) -> str:
        return "Scheduled Job"

    def list_running(
        self, projects: List[Project]
    ) -> List[Execution[ScheduledJobId]]:
        running_executions = []
        for project in projects:
            jobs = self.get(f"/v4/projects/{project._id}/scheduledjobs")
            for job in jobs:
                if not job["isPaused"]:
                    running_executions.append(
                        Execution(
                            ScheduledJobId(job["id"], job["projectId"]),
                            job["title"],
                            job["scheduledByUserName"],
                        )
                    )
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