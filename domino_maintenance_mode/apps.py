import logging
import os
from pprint import pformat
from typing import List

import requests

from domino_maintenance_mode.shutdown_manager import (
    Execution,
    ExecutionTypeInterface,
)

logger = logging.getLogger(__name__)

STOPPED_STATES = {"Stopped"}
RUNNING_STATES = {"Running"}


class AppInterface(ExecutionTypeInterface):
    api_key = os.environ["DOMINO_API_KEY"]
    hostname = os.environ["DOMINO_HOSTNAME"]

    def list_running(self) -> List[Execution]:
        data = requests.get(
            f"{self.hostname}/v4/modelProducts",
            headers={
                "Content-Type": "application/json",
                "X-Domino-Api-Key": self.api_key,
            },
        ).json()
        executions = []
        for app in data:
            logger.info(pformat(app))
            try:
                if app["status"] in STOPPED_STATES:
                    continue
                executions.append(
                    Execution(
                        app["id"], app["name"], app["publisher"]["userName"]
                    )
                )
            except Exception as e:
                logger.warn(f"Error parsing App: '{pformat(app)}': {e}")
        return executions

    def stop(self, _id: str):
        response = requests.post(
            f"{self.hostname}/v4/modelProducts/{_id}/stop",
            headers={
                "Content-Type": "application/json",
                "X-Domino-Api-Key": self.api_key,
            },
        )
        logger.debug(response.text)
        assert response.status_code == 200

    def start(self, _id: str):
        response = requests.post(
            f"{self.hostname}/v4/modelProducts/{_id}/start",
            headers={
                "Content-Type": "application/json",
                "X-Domino-Api-Key": self.api_key,
            },
        )
        logger.debug(response.text)
        assert response.status_code == 200

    def is_stopped(self, _id: str) -> bool:
        data = requests.get(
            f"{self.hostname}/v4/modelProducts/{_id}",
            headers={
                "Content-Type": "application/json",
                "X-Domino-Api-Key": self.api_key,
            },
        ).json()
        logger.debug(pformat(data))
        return data["status"] in STOPPED_STATES

    def is_running(self, _id: str) -> bool:
        data = requests.get(
            f"{self.hostname}/v4/modelProducts/{_id}",
            headers={
                "Content-Type": "application/json",
                "X-Domino-Api-Key": self.api_key,
            },
        ).json()
        logger.debug(pformat(data))
        return data["status"] in RUNNING_STATES
