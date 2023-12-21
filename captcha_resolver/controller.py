import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
from fastapi import Request
import json

from starlette.responses import FileResponse

from captcha_resolver.models.capcha import *
from fastapi import Response
import time
from captcha_resolver.init import instance_id
import time

def init_routes(app, service):

    @app.get("/hello")
    async def hello():
        return json.dumps({"hello": "world"})

    @app.post("/get_captchas")
    async def get_solve_torch(request: RequestModel):
        start = time.time()
        sequence, error = service.get_captcha_solve_sequence_hybrid_merge_business(
            request=request)
        end = time.time()
        try:
            with open('captcha_resolver/logs/' + str(instance_id) + '.txt', 'a') as f:
                f.write('\n')
                f.write('Time_taken: '+str(end-start))
        except Exception as e:
            print(e)

        if error:
            return Response(content=json.dumps({"status": 0, "request": "ERROR_CAPTCHA_UNSOLVABLE"}), media_type="application/json")
        return Response(content=json.dumps({"status": 1, "request": sequence}), media_type="application/json")

    @app.post("/get_captchas1")
    async def get_solve_onnx(request: RequestModel):
        start = time.time()
        sequence, error = service.get_onnx_solver(request)
        end = time.time()
        try:
            with open('captcha_resolver/logs/' + str(instance_id) + '.txt', 'a') as f:
                f.write('\n')
                f.write('Time_taken: ' + str(end - start))
        except Exception as e:
            print(e)
        if error:
            return Response(content=json.dumps({"status": 0, "request": "ERROR_CAPTCHA_UNSOLVABLE"}),
                            media_type="application/json")
        return Response(content=json.dumps({"status": 1, "request": sequence}), media_type="application/json")

    @app.get("/get_unresolved_captchas")
    async def get_unresolved_captchas():
        service.get_unresolved_captchas()
        file_path = 'captchas.zip'
        return FileResponse(path=file_path, filename=file_path, media_type='text/mp4')

    @app.get("/delete_unresolved_captchas")
    async def delete_unresolved_captchas():
        service.delete_unresolved_captchas()
