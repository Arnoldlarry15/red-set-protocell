"""Early-access signup persistence model and helpers."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""

    pass


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "early_access_signups.db"
DATABASE_URL = os.getenv("RSP_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")


def _create_engine(database_url: str):
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            future=True,
        )
    return create_engine(database_url, future=True)


engine = _create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class EarlyAccessSignup(Base):
    """SQLAlchemy ORM model for early-access signups."""

    __tablename__ = "early_access_signups"

    id = mapped_column(Integer, primary_key=True, index=True)
    email = mapped_column(String(320), unique=True, nullable=False, index=True)
    role = mapped_column(String(64), nullable=True, index=True)
    status = mapped_column(String(32), nullable=False, default="pending", index=True)
    submitted_at = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    verified_at = mapped_column(DateTime(timezone=True), nullable=True)


def init_early_access_db() -> None:
    """Create the early-access signup table if it does not already exist."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session with commit/rollback handling."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _to_iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def serialize_signup(signup: EarlyAccessSignup) -> Dict[str, Any]:
    """Serialize an ORM signup object into API-safe JSON."""
    return {
        "id": signup.id,
        "email": signup.email,
        "role": signup.role,
        "status": signup.status,
        "submitted_at": _to_iso(signup.submitted_at),
        "created_at": _to_iso(signup.created_at),
        "updated_at": _to_iso(signup.updated_at),
        "verified_at": _to_iso(signup.verified_at),
    }


def create_signup(email: str, role: Optional[str], submitted_at: datetime) -> Dict[str, Any]:
    """Insert a signup row and return the serialized record."""
    with db_session() as session:
        signup = EarlyAccessSignup(
            email=email,
            role=role,
            submitted_at=submitted_at,
            status="pending",
        )
        session.add(signup)
        try:
            session.flush()
        except IntegrityError as exc:
            raise ValueError("Signup already exists for this email") from exc
        session.refresh(signup)
        return serialize_signup(signup)


def list_signups(
    *,
    page: int,
    page_size: int,
    role: Optional[str] = None,
    status: Optional[str] = None,
    email_query: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return paginated signups with optional filtering."""
    with db_session() as session:
        query = session.query(EarlyAccessSignup)
        if role:
            query = query.filter(EarlyAccessSignup.role == role)
        if status:
            query = query.filter(EarlyAccessSignup.status == status)
        if email_query:
            query = query.filter(EarlyAccessSignup.email.ilike(f"%{email_query}%"))
        if start_date:
            query = query.filter(EarlyAccessSignup.submitted_at >= start_date)
        if end_date:
            query = query.filter(EarlyAccessSignup.submitted_at <= end_date)

        total = query.count()
        rows = (
            query.order_by(EarlyAccessSignup.submitted_at.desc(), EarlyAccessSignup.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {"count": total, "signups": [serialize_signup(row) for row in rows]}


def list_all_signups(
    *,
    role: Optional[str] = None,
    status: Optional[str] = None,
    email_query: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[Dict[str, Any]]:
    """Return all signups for export."""
    with db_session() as session:
        query = session.query(EarlyAccessSignup)
        if role:
            query = query.filter(EarlyAccessSignup.role == role)
        if status:
            query = query.filter(EarlyAccessSignup.status == status)
        if email_query:
            query = query.filter(EarlyAccessSignup.email.ilike(f"%{email_query}%"))
        if start_date:
            query = query.filter(EarlyAccessSignup.submitted_at >= start_date)
        if end_date:
            query = query.filter(EarlyAccessSignup.submitted_at <= end_date)
        rows = query.order_by(EarlyAccessSignup.submitted_at.desc(), EarlyAccessSignup.id.desc()).all()
        return [serialize_signup(row) for row in rows]


def verify_signup(signup_id: int) -> Dict[str, Any]:
    """Mark a signup as verified and return it."""
    with db_session() as session:
        signup = session.get(EarlyAccessSignup, signup_id)
        if not signup:
            raise LookupError("Signup not found")
        signup.status = "verified"
        signup.verified_at = datetime.now(timezone.utc)
        signup.updated_at = datetime.now(timezone.utc)
        session.add(signup)
        session.flush()
        session.refresh(signup)
        return serialize_signup(signup)


def delete_signup(signup_id: int) -> Dict[str, Any]:
    """Delete a signup row and return the deleted data."""
    with db_session() as session:
        signup = session.get(EarlyAccessSignup, signup_id)
        if not signup:
            raise LookupError("Signup not found")
        serialized = serialize_signup(signup)
        session.delete(signup)
        session.flush()
        return serialized
