import os
import socket

from fastapi import FastAPI

app = FastAPI(title="python-app")

# 版本号由流水线在部署时通过环境变量注入
APP_VERSION = os.getenv("APP_VERSION", "dev")


@app.get("/")
async def index() -> dict:
    # pod 字段是主机名，也就是 Pod 名，刷新可看到负载均衡到不同副本
    return {
        "app": "python-app", 
        "version": APP_VERSION, 
        "pod": socket.gethostname(), 
        "message": "hello webhook",
        "banner": "v4-new-feature",  # 这是我们新增的业务特性
        }


@app.get("/healthz")
async def healthz() -> dict:
    # 给 K8s 就绪探针使用
    return {"status": "ok"}
