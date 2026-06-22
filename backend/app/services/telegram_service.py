from __future__ import annotations

import httpx

from app.core.config import get_settings


async def send_telegram_message(text: str) -> bool:
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_dispatch_chat_id:
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            url,
            json={
                "chat_id": settings.telegram_dispatch_chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
        )
        response.raise_for_status()
    return True
