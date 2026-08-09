## @file database.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Database engine and session management (the single shared SQLModel engine).
#
"""Database engine and session management.

Centralises the single SQLModel 'engine' and exposes:
  - 'create_tables()' : create the schema on startup (POC convenience;
    Alembic migrations are the production path),
  - 'get_session()'   : a FastAPI dependency that yields a scoped session and
    guarantees it is closed after each request.
"""

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL, DEBUG

# One engine per process. 'echo=DEBUG' logs every SQL statement in
# development, which is invaluable while building, and stays silent otherwise.
engine = create_engine(DATABASE_URL, echo=DEBUG)

## @fn create_tables()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Create every table registered on SQLModel's metadata.
#  @return None. Tables are created as a side effect on the configured engine.
#
def create_tables() -> None:
    """Create all tables registered on 'SQLModel.metadata'.

    The model modules must be imported *before* 'create_all' runs, otherwise
    their tables are not yet registered on the shared metadata. We import them
    here (locally, to avoid a circular import at module load time) purely for
    that registration side effect.
    """
    from app.models import order, rule

    SQLModel.metadata.create_all(engine)

## @fn get_session()
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Yield a database session for the lifetime of a single request (FastAPI dependency).
#  @return An Iterator yielding one SQLModel Session, closed automatically when the request ends.
#
def get_session() -> Iterator[Session]:
    """Yield a database session for the lifetime of a single request.

    Used as a FastAPI dependency (session: Session = Depends(get_session)).
    The 'with' block ensures the session  and its connection  is always
    returned to the pool, even if the request handler raises.
    """
    with Session(engine) as session:
        yield session
