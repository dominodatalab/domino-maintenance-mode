import os


def get_api_key() -> str:
    if "DOMINO_API_KEY" not in os.environ:
        raise Exception(
            (
                "Please specify Domino API key using "
                "'DOMINO_API_KEY' environment variable."
            )
        )
    return os.environ["DOMINO_API_KEY"]


def get_hostname() -> str:
    if "DOMINO_HOSTNAME" not in os.environ:
        raise Exception(
            (
                "Please specify Domino deployment hostname"
                " using 'DOMINO_HOSTNAME' environment variable."
            )
        )
    return os.environ["DOMINO_HOSTNAME"]
