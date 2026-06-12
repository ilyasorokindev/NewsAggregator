import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.source import SourceCreate, SourceDelete, SourceResponse, SourceUpdate
from app.services import ingestion_service, source_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/setup")


@router.get("/items", response_model=list[SourceResponse])
def list_items(db: Session = Depends(get_db)):
    return source_service.list_sources(db)


@router.post("/item", response_model=SourceResponse, status_code=201)
async def create_item(body: SourceCreate, db: Session = Depends(get_db)):
    try:
        source = source_service.create_source(db, str(body.url))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    asyncio.create_task(_scrape_one(source.guid))
    return source


@router.put("/item", response_model=SourceResponse)
async def update_item(body: SourceUpdate, db: Session = Depends(get_db)):
    try:
        source = source_service.update_source(db, body.guid, str(body.url))
    except LookupError:
        raise HTTPException(status_code=404, detail="Source not found")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    ingestion_service.delete_source_chunks(body.guid)
    asyncio.create_task(_scrape_one(source.guid))
    return source


@router.delete("/item", status_code=204)
def delete_item(body: SourceDelete, db: Session = Depends(get_db)):
    try:
        source = source_service.get_source(db, body.guid)
        if source is None:
            raise LookupError(body.guid)
        ingestion_service.delete_source_chunks(body.guid)
        source_service.delete_source(db, body.guid)
    except LookupError:
        raise HTTPException(status_code=404, detail="Source not found")


async def _scrape_one(source_guid: str) -> None:
    from app.database import SessionLocal
    from app.models.source import NewsSource
    from app.services.ingestion_service import _scrape_source
    with SessionLocal() as db:
        source = db.query(NewsSource).filter(NewsSource.guid == source_guid).first()
    if source:
        await _scrape_source(source)
