from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class FrontendLogData(BaseModel):
    level: str = Field(..., description="Уровень лога: info, warn, error")
    message: str = Field(..., description="Сообщение лога")
    context: Optional[Dict[str, Any]] = Field(None, description="Дополнительный контекст ошибки")
    url: str = Field(..., description="URL страницы, где произошла ошибка")
    userAgent: str = Field(..., description="ОС и версия браузера пользователя")
    timestamp: str = Field(..., description="Время возникновения события")
