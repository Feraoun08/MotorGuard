
from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session


def get_db_session(
    request: Request,
) -> Generator[Session, None, None]:
    """
    Provide a database session for one API request.

    The session is always closed after the request completes.
    """

    session_factory = request.app.state.session_factory

    session = session_factory()

    try:
        yield session
    finally:
        session.close()
