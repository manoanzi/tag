from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.protocols.http_server import Handler


class FastAPIDriver:
    """Implements the HttpServer Protocol with FastAPI."""

    def __init__(self) -> None:
        self.app = FastAPI(title="TAG user service example")

    def post(self, path: str, handler: Handler) -> None:
        async def route(request: Request) -> JSONResponse:
            body: Any = await request.json()
            status, payload = handler(body if isinstance(body, dict) else {})
            return JSONResponse(status_code=status, content=payload)

        self.app.add_api_route(path, route, methods=["POST"])

    def start(self, port: int) -> None:
        uvicorn.run(self.app, host="0.0.0.0", port=port)
