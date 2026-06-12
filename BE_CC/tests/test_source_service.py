import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import source as _  # register model
from app.services.source_service import (
    create_source,
    delete_source,
    get_source,
    list_sources,
    update_source,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_and_list(db):
    create_source(db, "https://example.com")
    sources = list_sources(db)
    assert len(sources) == 1
    assert sources[0].url == "https://example.com"


def test_create_assigns_guid(db):
    source = create_source(db, "https://example.com")
    assert source.guid is not None
    assert len(source.guid) == 36  # UUID4 format


def test_duplicate_url_raises(db):
    create_source(db, "https://example.com")
    with pytest.raises(ValueError):
        create_source(db, "https://example.com")


def test_get_source(db):
    source = create_source(db, "https://example.com")
    found = get_source(db, source.guid)
    assert found is not None
    assert found.url == "https://example.com"


def test_get_source_not_found(db):
    assert get_source(db, "nonexistent-guid") is None


def test_update_source(db):
    source = create_source(db, "https://example.com")
    updated = update_source(db, source.guid, "https://updated.com")
    assert updated.url == "https://updated.com"
    assert updated.guid == source.guid


def test_update_source_not_found(db):
    with pytest.raises(LookupError):
        update_source(db, "bad-guid", "https://example.com")


def test_update_url_conflict(db):
    create_source(db, "https://a.com")
    b = create_source(db, "https://b.com")
    with pytest.raises(ValueError):
        update_source(db, b.guid, "https://a.com")


def test_delete_source(db):
    source = create_source(db, "https://example.com")
    delete_source(db, source.guid)
    assert get_source(db, source.guid) is None


def test_delete_source_not_found(db):
    with pytest.raises(LookupError):
        delete_source(db, "bad-guid")
