from fastapi import APIRouter, Request
import structlog
from app.schemas.log import FrontendLogData

router = APIRouter()
logger = structlog.get_logger("frontend_logger")

@router.post("", status_code=200)
async def receive_frontend_log(log_data: FrontendLogData, request: Request):
    """
    Эндпоинт для приема логов с фронтенда.
    Логи пишутся в системный вывод с пометкой frontend_logger.
    """
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            import jwt
            from app.core.config import settings
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
        except Exception:
            pass

    log_context = {
        "url": log_data.url,
        "userAgent": log_data.userAgent,
        "frontend_timestamp": log_data.timestamp,
        "frontend_context": log_data.context,
        "user_id": user_id
    }
    
    if log_data.level == "error":
        logger.error(log_data.message, **log_context)
    elif log_data.level in ["warn", "warning"]:
        logger.warning(log_data.message, **log_context)
    else:
        logger.info(log_data.message, **log_context)
        
    return {"status": "success", "message": "Log received"}
