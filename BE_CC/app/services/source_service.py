import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.source import NewsSource


def list_sources(db: Session) -> list[NewsSource]:
    return db.query(NewsSource).all()


def get_source(db: Session, guid: str) -> NewsSource | None:
    return db.query(NewsSource).filter(NewsSource.guid == guid).first()


def create_source(db: Session, url: str) -> NewsSource:
    source = NewsSource(guid=str(uuid.uuid4()), url=url)
    db.add(source)
    try:
        db.commit()
        db.refresh(source)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"URL already exists: {url}")
    return source


def update_source(db: Session, guid: str, url: str) -> NewsSource:
    source = get_source(db, guid)
    if source is None:
        raise LookupError(guid)
    source.url = url
    try:
        db.commit()
        db.refresh(source)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"URL already exists: {url}")
    return source


def delete_source(db: Session, guid: str) -> None:
    source = get_source(db, guid)
    if source is None:
        raise LookupError(guid)
    db.delete(source)
    db.commit()
