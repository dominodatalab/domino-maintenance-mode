import setuptools  # type: ignore

setuptools.setup(
    name="domino_maintenance_mode",
    version="0.1.0",
    author="Kevin Flansburg",
    author_email="kevin.flansburg@dominodatalab.com",
    description=(
        "Easily place Domino in maintenance mode for"
        " upgrades and restore afterwards."
    ),
    url="https://github.com/dominodatalab/domino-maintenance-mode",
    packages=setuptools.find_packages(),
    install_requires=[
        "click",
        "requests",
        "tqdm",
        "asyncio",
        "aiohttp",
        "types-requests",
    ],
    entry_points={
        "console_scripts": ["dmm = domino_maintenance_mode.cli:main"]
    },
)
