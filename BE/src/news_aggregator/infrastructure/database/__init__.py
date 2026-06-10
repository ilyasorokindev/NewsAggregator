from news_aggregator.infrastructure.database.base import Base
from news_aggregator.infrastructure.database.constants import DEFAULT_EMBEDDING_DIMENSION
from news_aggregator.infrastructure.database.mappers import (
    news_chunk_to_entity,
    search_result_from_row,
    search_results_from_rows,
    source_to_entity,
)
from news_aggregator.infrastructure.database.session import (
    create_engine,
    create_session_factory,
    dispose_session_manager,
    get_db_session,
    get_session_manager,
    init_session_manager,
)
from news_aggregator.infrastructure.database.session_manager import DatabaseSessionManager
from news_aggregator.infrastructure.database.text_hash import compute_text_hash
from news_aggregator.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork

__all__ = [
    "Base",
    "DEFAULT_EMBEDDING_DIMENSION",
    "DatabaseSessionManager",
    "SqlAlchemyUnitOfWork",
    "compute_text_hash",
    "create_engine",
    "create_session_factory",
    "dispose_session_manager",
    "get_db_session",
    "get_session_manager",
    "init_session_manager",
    "news_chunk_to_entity",
    "search_result_from_row",
    "search_results_from_rows",
    "source_to_entity",
]
