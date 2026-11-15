import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.api.routes.analyses import router as analyses_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)

app = FastAPI(title="after meeting API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(analyses_router, prefix="/api")


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "Handled API error code=%s status=%s path=%s",
        exc.code,
        exc.status_code,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "action": exc.action,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_REQUEST",
                "message": "요청에 필요한 파일이 없거나 요청 형식이 올바르지 않습니다.",
                "action": "TXT 파일을 첨부해 다시 요청해 주세요.",
            }
        },
    )
