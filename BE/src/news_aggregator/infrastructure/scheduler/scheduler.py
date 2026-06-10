import logging
from collections.abc import Callable, Coroutine
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from news_aggregator.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


class SchedulerBootstrap:
    """Bootstrap and manage APScheduler background jobs."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._scheduler = AsyncIOScheduler()

    def register_sync_job(
        self,
        job: Callable[[], Coroutine[Any, Any, None]],
    ) -> None:
        """Register the feed synchronization job."""
        self._scheduler.add_job(
            job,
            trigger=IntervalTrigger(minutes=self._settings.sync_interval_minutes),
            id="feed_sync",
            replace_existing=True,
        )
        logger.info(
            "Registered feed sync job",
            extra={"interval_minutes": self._settings.sync_interval_minutes},
        )

    def start(self) -> None:
        """Start the scheduler after application startup."""
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        """Shutdown the scheduler gracefully."""
        self._scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
