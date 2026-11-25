"""SyntaxSense HTTP API."""

from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StrictStr
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.logging_config import get_logger, setup_logging
from backend.app.services.cpp_analysis import MAX_SOURCE_LENGTH
from backend.app.services.registry import (
    UnsupportedLanguageError,
    get_default_registry,
)

# Initialize centralized logging
setup_logging()
logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry = get_default_registry()
    logger.info(
        "SyntaxSense API startup complete [service=FastAPI, version=0.2.0, supported=%s, planned=%s]",
        ", ".join(registry.supported_languages),
        ", ".join(registry.planned_languages),
    )
    yield
    logger.info("SyntaxSense API shutting down")


app = FastAPI(title="SyntaxSense API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.get("/api/v1/health")
def healthcheck():
    logger.debug("Healthcheck endpoint requested")
    registry = get_default_registry()
    return {
        "status": "ok",
        "service": "SyntaxSense API",
        "version": "0.2.0",
        "supportedLanguages": registry.supported_languages,
        "plannedLanguages": registry.planned_languages,
        "supportedLanguage": "cpp",  # Kept for backward compatibility
    }


class AnalyzeRequest(BaseModel):
    language: StrictStr
    code: StrictStr = Field(min_length=1, max_length=MAX_SOURCE_LENGTH)


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Request validation failed: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_request",
                "message": "Request must contain string fields 'language' and 'code'; code must not exceed the source limit.",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("HTTP %d exception: %s", exc.status_code, exc.detail)
    return error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
    )


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled server exception: %s", exc)
    return error_response(
        status_code=500,
        code="internal_server_error",
        message=f"Internal server error: {exc}" if str(exc) else "An unexpected internal server error occurred.",
    )


@app.post("/api/v1/analyze")
def analyze(request: AnalyzeRequest):
    code_length = len(request.code)
    logger.info(
        "Received analyze request: language='%s', payload_size=%d chars",
        request.language,
        code_length,
    )

    registry = get_default_registry()
    try:
        analyzer = registry.get_analyzer(request.language)
        logger.debug("Dispatched to analyzer: %s (%s)", analyzer.language_id, type(analyzer).__name__)
    except UnsupportedLanguageError as exc:
        is_planned = exc.language.lower() in [p.lower() for p in exc.planned]
        err_code = "planned_language" if is_planned else "unsupported_language"
        err_msg = (
            f"Language '{exc.language}' is planned for future release but not yet implemented."
            if is_planned
            else f"Language '{exc.language}' is not supported. Supported languages: {', '.join(exc.supported)}."
        )
        logger.warning(
            "Rejected %s language request '%s' (supported=%s)",
            "planned" if is_planned else "unsupported",
            exc.language,
            ", ".join(exc.supported),
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": err_code,
                    "message": err_msg,
                    "supportedLanguages": exc.supported,
                    "plannedLanguages": exc.planned,
                }
            },
        )
    except Exception as exc:
        logger.exception("Failed to obtain analyzer for '%s': %s", request.language, exc)
        return error_response(500, "analyzer_init_failed", str(exc))

    try:
        start_time = time.perf_counter()
        result = analyzer.analyze(request.code)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Analysis completed: language='%s', duration=%.2fms, label='%s', diagnostics=%d",
            request.language,
            duration_ms,
            result.get("classification", {}).get("label"),
            result.get("summary", {}).get("diagnosticCount", 0),
        )
        return result
    except (TypeError, ValueError) as exc:
        logger.warning("Invalid source code rejected for '%s': %s", request.language, exc)
        return error_response(422, "invalid_source", str(exc))
    except Exception as exc:
        lang_display = "C++" if request.language.lower() == "cpp" else request.language.capitalize()
        logger.exception(
            "Unhandled exception during %s analysis (payload_size=%d chars): %s",
            lang_display,
            code_length,
            exc,
        )
        return error_response(
            500,
            "analysis_failed",
            f"{lang_display} analysis could not be completed.",
        )
