from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.truck import TruckListOut
from app.services.truck_broadcaster import truck_broadcaster
from app.services.truck_service import list_trucks

router = APIRouter()


@router.get("", response_model=TruckListOut)
async def api_list_trucks(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = Query(500, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> TruckListOut:
    total, trucks = await list_trucks(session, search=search, status_filter=status_filter, limit=limit, offset=offset)
    return TruckListOut(total=total, items=trucks)


@router.get("/stream")
async def api_truck_stream() -> StreamingResponse:
    async def event_stream():
        async for event in truck_broadcaster.subscribe():
            yield f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
