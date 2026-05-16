"""JWT helpers.

Deprecated: используйте app.core.security напрямую.
Сохранено для обратной совместимости импортов.
"""

from app.core.security import create_access_token, verify_token

__all__ = ["create_access_token", "verify_token"]