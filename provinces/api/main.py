import os
import sys

from fastapi import FastAPI
from logbook import Logger, StreamHandler
from logbook.more import ColorizedStderrHandler
from pydantic_settings import BaseSettings
from starlette.middleware.cors import CORSMiddleware

from . import __version__
from .v1 import api_v1
from .config import settings


class Settings(BaseSettings):
    tracking: bool = False


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

if settings.ENV == 'production':
    app.mount('/', api_v1)
else:
    app.mount('/api/v1', api_v1)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host=settings.HOST, port=settings.PORT, reload=True, log_level='debug')