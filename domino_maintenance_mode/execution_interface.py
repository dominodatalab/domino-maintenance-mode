from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

import aiohttp
import backoff
import requests

from domino_maintenance_mode.projects import Project
from domino_maintenance_mode.util import (
    get_api_key,
    get_hostname,
    should_verify,
)

Id = TypeVar("Id")


@dataclass
class Execution(Generic[Id]):
    _id: Id
    name: str
    owner: str


@dataclass
class FailedExecution(Generic[Id]):
    execution: Execution[Id]
    message: str


class ExecutionInterface(ABC, Generic[Id]):
    session: Optional[requests.Session] = None
    async_session: Optional[aiohttp.ClientSession] = None

    def __init__(self, **kwargs):
        pass

    def __get_session(self) -> requests.Session:
        if self.session is None:
            api_key = get_api_key()
            self.hostname = get_hostname()
            # TODO: Ability to trust custom certs?
            self.session = requests.Session()
            self.session.headers.update(
                {
                    "Content-Type": "application/json",
                    "X-Domino-Api-Key": api_key,
                }
            )
            self.session.verify = should_verify()
        return self.session

    def id_from_value(self, v) -> Id:
        # Override for non-primitive Id types
        return v

    def execution_from_dict(self, d: dict) -> Execution[Id]:
        return Execution(self.id_from_value(d["_id"]), d["name"], d["owner"])

    def get(self, path: str, success_code: int = 200) -> dict:
        response = self.__get_session().get(f"{self.hostname}{path}")
        if response.status_code != success_code:
            raise Exception(
                f"API returned error ({response.status_code}): {response.text}"
            )
        return response.json()

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        jitter=backoff.random_jitter,
        factor=0.5,
    )
    async def async_get(
        self,
        session: aiohttp.ClientSession,
        path: str,
        success_code: int = 200,
    ) -> dict:
        api_key = get_api_key()
        hostname = get_hostname()
        verify = should_verify()

        try:
            url = f"{hostname}{path}"

            async with session.get(
                url=url,
                headers={
                    "Content-Type": "application/json",
                    "X-Domino-Api-Key": api_key,
                },
                verify_ssl=verify,
            ) as response:
                resp = await response.text()
                if response.status != success_code:
                    raise Exception(
                        f"API ({url}) returned error ({response.status}): {resp}"
                    )
                return await response.json()
        except Exception as e:
            print(f"Unable to get url {path} due to {e}.")
            raise e

    def post(
        self, path: str, json: Optional[dict] = None, success_code: int = 200
    ) -> dict:
        url = f"{self.hostname}{path}"

        response = self.__get_session().post(url, json=json)
        if response.status_code != success_code:
            raise Exception(
                f"API ({url}) returned error({response.status_code}): {response.text}"
            )
        return response.json()

    def put(
        self, path: str, json: Optional[dict] = None, success_code: int = 200
    ) -> dict:
        url = f"{self.hostname}{path}"

        response = self.__get_session().put(url, json=json)
        if response.status_code != success_code:
            raise Exception(
                f"API ({url}) returned error ({response.status_code}): {response.text}"
            )
        return response.json()

    @abstractmethod
    def singular(self) -> str:
        pass

    @abstractmethod
    async def list_running(
        self, session: aiohttp.ClientSession, projects: List[Project]
    ) -> List[Execution[Id]]:
        """List non-stopped (running or pending) executions."""
        pass

    @abstractmethod
    def stop(self, _id: Id):
        """Initiate shutdown of an execution. Throws exception on failure."""
        pass

    @abstractmethod
    def start(self, _id: Id):
        """Initiate launch of an execution. Throws exception on failure."""
        pass

    @abstractmethod
    def is_running(self, _id: Id) -> bool:
        """Is the execution in a stopped state."""
        pass

    @abstractmethod
    def is_stopped(self, _id: Id) -> bool:
        """Is the execution fully running."""
        pass

    @abstractmethod
    def is_restartable(self) -> bool:
        """Should this execution type be restarted after
        the maintenance window.
        """
        pass
