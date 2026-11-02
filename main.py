import os
import socket

from fastapi import FastAPI

app = FastAPI(title="python-app")

APP_ENV = os.getenv("APP_ENV", "local")
APP_VERSION = os.getenv("APP_VERSION", "dev")


@app.get("/")
async def index() -> dict:
    return {
        "app": "python-app",
        "env": APP_ENV,
        "version": APP_VERSION,
        "pod": socket.gethostname(),
        "message": "hello gitops v2 auto-deploy",
    }


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}
