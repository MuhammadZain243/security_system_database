"""SQLAlchemy engine, session factory, and transaction helpers."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from security_system_database.config import DatabaseSettings, get_database_settings

SessionFactory = sessionmaker[Session]


def build_engine(settings: DatabaseSettings | None = None) -> Engine:
    """Create the process-level SQLAlchemy engine."""

    resolved_settings = settings or get_database_settings()

    return create_engine(
        resolved_settings.sqlalchemy_url,
        echo=resolved_settings.echo,
        pool_pre_ping=True,
        pool_size=resolved_settings.pool_size,
        max_overflow=resolved_settings.max_overflow,
        pool_timeout=resolved_settings.pool_timeout_seconds,
        pool_recycle=resolved_settings.pool_recycle_seconds,
        connect_args={
            "connect_timeout": resolved_settings.connect_timeout_seconds,
        },
    )


def build_session_factory(engine: Engine) -> SessionFactory:
    """Create a reusable SQLAlchemy session factory."""

    return sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


@contextmanager
def tenant_session(
    session_factory: SessionFactory,
    tenant_id: UUID | str,
) -> Iterator[Session]:
    """Open a transaction with a transaction-local tenant context."""

    validated_tenant_id = UUID(str(tenant_id))

    with session_factory() as session, session.begin():
        session.execute(
            text(
                """
                    SELECT set_config(
                        'app.current_tenant_id',
                        :tenant_id,
                        true
                    )
                    """
            ),
            {"tenant_id": str(validated_tenant_id)},
        )

        yield session


@contextmanager
def platform_session(session_factory: SessionFactory) -> Iterator[Session]:
    """Open a transaction without setting tenant context."""

    with session_factory() as session, session.begin():
        yield session
