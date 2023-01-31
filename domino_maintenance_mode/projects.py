import logging
from dataclasses import dataclass
from typing import List

import aiohttp

from domino_maintenance_mode.util import (
    get_api_key,
    get_hostname,
    should_verify,
)

logger = logging.getLogger(__name__)


@dataclass
class Project:
    _id: str
    name: str
    owner: str


async def fetch_projects() -> List[Project]:
    api_key = get_api_key()
    hostname = get_hostname()
    verify = should_verify()
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"{hostname}/v4/projects",
            headers={
                "Content-Type": "application/json",
                "X-Domino-Api-Key": api_key,
            },
            verify_ssl=verify,
        ) as response:
            data = await response.json()
            logger.info(f"Found {len(data)}.")
            return list(
                map(
                    lambda project: Project(
                        project["id"],
                        project["name"],
                        project["ownerUsername"],
                    ),
                    data,
                )
            )
