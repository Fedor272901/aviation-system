"""Утилиты для API слоя."""

from fastapi import HTTPException, status


def raise_from_value_error(e: ValueError) -> None:
    """Преобразует ValueError из сервисов в HTTPException с семантичным кодом."""
    msg = str(e).lower()
    if any(s in msg for s in ("не найден", "не найдена", "не найдено")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if any(s in msg for s in (
        "уже существует", "уже занят", "уже зарегистрирован",
        "уже является", "уже назначен", "уже есть",
    )):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))