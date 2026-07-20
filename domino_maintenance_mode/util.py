import asyncio
import os
from typing import Dict

AUTH_TOKEN_ENV = "DOMINO_AUTH_TOKEN"
API_KEY_ENV = "DOMINO_API_KEY"


def _is_jwt(value: str) -> bool:
    """Keycloak bearer tokens (e.g. Personal Access Tokens) are JWTs:
    three dot-separated segments with an 'eyJ' header prefix. Legacy
    Domino API keys are opaque strings and never match this shape."""
    return value.startswith("eyJ") and len(value.split(".")) == 3


def get_auth_headers() -> Dict[str, str]:
    """Resolve the Domino credential and return its auth header.

    Resolution order:
    1. DOMINO_AUTH_TOKEN -> 'Authorization: Bearer <token>' (a Personal
       Access Token, available since Domino 6.3.0, or any Keycloak
       bearer token).
    2. DOMINO_API_KEY -> 'X-Domino-Api-Key' (legacy admin API key).
       A JWT-shaped value here is sent as a bearer token instead: a PAT
       placed in DOMINO_API_KEY would otherwise be sent as a legacy key
       and rejected by the API as an anonymous request.
    """
    token = os.environ.get(AUTH_TOKEN_ENV)
    if token:
        return {"Authorization": f"Bearer {token}"}

    api_key = os.environ.get(API_KEY_ENV)
    if api_key:
        if _is_jwt(api_key):
            return {"Authorization": f"Bearer {api_key}"}
        return {"X-Domino-Api-Key": api_key}

    raise Exception(
        (
            "No Domino credential found. Set 'DOMINO_AUTH_TOKEN' to a "
            "Personal Access Token (Domino 6.3.0+), or "
            "'DOMINO_API_KEY' to an administrator's legacy API key."
        )
    )


def get_hostname() -> str:
    if "DOMINO_HOSTNAME" not in os.environ:
        raise Exception(
            (
                "Please specify Domino deployment hostname"
                " using 'DOMINO_HOSTNAME' environment variable."
            )
        )
    return os.environ["DOMINO_HOSTNAME"]


def should_verify() -> bool:
    return os.environ.get("DOMINO_SSL_NO_VERIFY") != "true"


async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))
