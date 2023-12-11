from fastapi import FastAPI
from captcha_resolver.controller import init_routes
from captcha_resolver.service import Service
app = FastAPI()
init_routes(app, Service())



