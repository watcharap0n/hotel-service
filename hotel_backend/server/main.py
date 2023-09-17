import logging
import os
import time
from datetime import datetime

import pytz
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

from .routes import auth, employee, guest, order

app = FastAPI(
    version=os.environ.get('SERVER_VERSION', '0.0.1'),
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    openapi_url='/api/openapi.json',
    include_in_schema=os.getenv('OPENAPI_SCHEMA', True),
)

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, 'static/')
os.makedirs(st_abs_file_path, exist_ok=True)
app.mount('/static', StaticFiles(directory=st_abs_file_path), name='static')

description = """
Hotel Document APIs Service. 👋🏻
"""

origins = [
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost:4000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log = logging.getLogger("uvicorn")
handler = Mangum(app)

app.include_router(
    auth.authenticate,
    prefix='/auth',
    tags=['auth']
)

app.include_router(
    order.router,
    prefix='/order',
    tags=['work-order']
)

app.include_router(
    employee.router,
    prefix='/employee',
    tags=['employee']
)

app.include_router(
    guest.router,
    prefix='/guest',
    tags=['guest']
)


@app.get('/404')
async def not_found_404():
    """
    Not found page

    :return:
    """
    return {'message': 'Not found page.'}


def customer_openapi():
    """
    docs description API
    :return:
        -> func
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Hotel Service",
        version=os.environ.get('SERVER_VERSION', '0.0.1'),
        description=description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = customer_openapi


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    """
    Protect vulnerabilities path traversal

    :param request:
    :param call_next:
    :return:
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    process_time = '{:2f}'.format(process_time)
    response.headers["X-Process-Time"] = str(process_time)
    pass_url = str(request.url)
    sentence = '../../' or '..%2F..%2F' or '/../../'
    if sentence in pass_url:
        return RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url='/404')
    return response


@app.on_event("startup")
async def startup_event():
    """Start up event for FastAPI application."""
    log.info("Starting up server")
    root_dir = os.path.dirname(__file__)
    static_dir = os.path.join(root_dir, 'static')
    log_dir = os.path.join(static_dir, 'log')
    os.makedirs(log_dir, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event for FastAPI application."""
    tz = pytz.timezone('Asia/Bangkok')
    dt = datetime.now(tz)
    timestamp = datetime.timestamp(dt)
    with open(f'{st_abs_file_path}/log/shutdown_event.txt', mode="w") as create_log:
        txt = f"""
        time: {dt} | timezone - asia/bangkok
        timestamp: {timestamp}
        Application shutdown server
        """
        create_log.write(txt)
    log.info("Shutting down...")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
