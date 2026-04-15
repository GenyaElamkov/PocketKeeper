from fastapi import FastAPI


def create_versions_app(version: str, title: str) -> FastAPI:
    version_app = FastAPI(
        title=title,
        description=f"API для PocketKeeper {version}",
        version=version,
    )
    return version_app
