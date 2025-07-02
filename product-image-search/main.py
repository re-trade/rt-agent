from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from dotenv import load_dotenv

from app.config import settings
from app.routes import image_analysis, similarity

app = FastAPI(
    title="ReTrade Bot API",
    description="Advanced AI Chatbot with Text, Image Analysis",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="ReTrade Bot API"
    )

@app.get("/ping")
async def ping_check():
    return {"status": "pong"}

def configure_app():
    settings.validate_config()
    app.include_router(image_analysis.router, tags=["Image Analysis"])
    app.include_router(similarity.router, tags=["Similarity Search"])


# if __name__ == '__main__':
# import uvicorn
configure_app()
# uvicorn.run(app, host="0.0.0.0", port=8000)

