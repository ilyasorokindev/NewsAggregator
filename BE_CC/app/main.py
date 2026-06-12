import asyncio
import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.config import settings
from app.database import init_db
from app.infrastructure.qdrant_client import ensure_collection
from app.routers import search, setup
from app.services.ingestion_service import run_ingestion

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()


async def _check_and_schedule_immediate() -> None:
    """Fire one ingestion pass within 10 s if Qdrant collection is empty."""
    from app.infrastructure.qdrant_client import get_qdrant_client
    client = get_qdrant_client()
    info = client.get_collection(settings.qdrant_collection)
    if info.points_count == 0:
        await asyncio.sleep(10)
        await run_ingestion()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ensure_collection()

    _scheduler.add_job(
        run_ingestion,
        "interval",
        minutes=settings.scrape_interval_minutes,
        max_instances=1,
        id="ingestion",
    )
    _scheduler.start()

    asyncio.create_task(_check_and_schedule_immediate())

    yield

    _scheduler.shutdown(wait=False)


app = FastAPI(title="News Aggregator", lifespan=lifespan)
app.include_router(search.router)
app.include_router(setup.router)
