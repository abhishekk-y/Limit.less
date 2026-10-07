from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

class BaseAPIException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class NotFound(BaseAPIException):
    def __init__(self, message="Not Found"):
        super().__init__(message, 404)

class Unauthorized(BaseAPIException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401)

class Forbidden(BaseAPIException):
    def __init__(self, message="Forbidden"):
        super().__init__(message, 403)

class Conflict(BaseAPIException):
    def __init__(self, message="Conflict"):
        super().__init__(message, 409)

class ValidationError(BaseAPIException):
    def __init__(self, message="Validation Error"):
        super().__init__(message, 422)

class TenantAccessDenied(BaseAPIException):
    def __init__(self, message="Tenant Access Denied"):
        super().__init__(message, 403)

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request: Request, exc: BaseAPIException):
        await logger.aerror("api_exception", error=exc.message, status_code=exc.status_code, path=request.url.path)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
