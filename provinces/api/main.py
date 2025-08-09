import os
import sys
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from logbook import Logger, StreamHandler
from logbook.more import ColorizedStderrHandler
from pydantic_settings import BaseSettings
from starlette.middleware.cors import CORSMiddleware

from . import __version__
from .v1 import api_v1


class Settings(BaseSettings):
    tracking: bool = False
    cdn_cache_interval: int = 30


logger = Logger(__name__)

if not os.getenv('VERCEL'):
    ColorizedStderrHandler().push_application()
else:
    StreamHandler(sys.stdout).push_application()


app = FastAPI(
    title='Vietnam Provinces online API',
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

settings = Settings()
app.mount('/', api_v1)


@app.middleware('http')
async def guide_cdn_cache(request: Request, call_next):
    response = await call_next(request)
    # Ref: https://vercel.com/docs/edge-network/headers#cache-control-header
    response.headers['Cache-Control'] = f's-maxage={settings.cdn_cache_interval}, stale-while-revalidate'
    return response
