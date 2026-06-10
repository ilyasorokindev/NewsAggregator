from news_aggregator.api.routers.health import router as health_router
from news_aggregator.api.routers.search import router as search_router
from news_aggregator.api.routers.setup import router as setup_router

__all__ = ["health_router", "search_router", "setup_router"]
