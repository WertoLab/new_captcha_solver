import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
from fastapi import Request
import json
from captcha_resolver.models.capcha import *
from fastapi import Response


def init_routes(app, service):

    @app.get("/hello")
    async def hello():
        return json.dumps({"hello": "world"})

    @app.post("/get_captchas1")
    async def get_solve_torch(request: RequestModel):
        sequence, error = service.get_captcha_solve_sequence_hybrid_merge_business(
            request=request)
        if error:
            return Response(content=json.dumps({"status": 0, "request": "ERROR_CAPTCHA_UNSOLVABLE"}), media_type="application/json")
        return Response(content=json.dumps({"status": 1, "request": sequence}), media_type="application/json")

    @app.post("/get_captchas")
    async def get_solve_onnx(request: RequestModel):
        sequence, error = service.get_onnx_solver(request)
        if error:
            return Response(content=json.dumps({"status": 0, "request": "ERROR_CAPTCHA_UNSOLVABLE"}),
                            media_type="application/json")
        return Response(content=json.dumps({"status": 1, "request": sequence}), media_type="application/json")
