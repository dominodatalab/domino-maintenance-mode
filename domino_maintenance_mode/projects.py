from dataclasses import dataclass
from typing import List

import requests

from domino_maintenance_mode.util import get_api_key, get_hostname


@dataclass
class Project:
    _id: str
    name: str
    owner: str


def fetch_projects() -> List[Project]:
    api_key = get_api_key()
    hostname = get_hostname()

    data = requests.get(
        f"{hostname}/v4/projects",
        headers={
            "Content-Type": "application/json",
            "X-Domino-Api-Key": api_key,
        },
    ).json()
    return list(
        map(
            lambda project: Project(
                project["id"], project["name"], project["ownerUsername"]
            ),
            data,
        )
    )
