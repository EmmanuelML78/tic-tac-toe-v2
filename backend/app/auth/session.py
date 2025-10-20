"""
Session management for reconnection support
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models import Session, User
from app.config import settings


class SessionManager:
    """Manage user sessions for reconnection"""

    @staticmethod
    async def create_session(
        user_id: int,
        token: str,
        socket_id: str,
        ip_address: str,
        user_agent: str,
        db: AsyncSession
    ) -> Session:
        """
        Create a new session

        Args:
            user_id: User ID
            token: JWT token
            socket_id: Socket.IO session ID
            ip_address: Client IP address
            user_agent: Client user agent
            db: Database session

        Returns:
            Created session object
        """
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        session = Session(
            id=session_id,
            user_id=user_id,
            token=token,
            socket_id=socket_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session_by_token(token: str, db: AsyncSession) -> Optional[Session]:
        """
        Get session by token

        Args:
            token: JWT token
            db: Database session

        Returns:
            Session object or None
        """
        result = await db.execute(
            select(Session).where(
                Session.token == token,
                Session.expires_at > datetime.utcnow()
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_sessions(user_id: int, db: AsyncSession) -> list[Session]:
        """
        Get all active sessions for a user

        Args:
            user_id: User ID
            db: Database session

        Returns:
            List of active sessions
        """
        result = await db.execute(
            select(Session).where(
                Session.user_id == user_id,
                Session.expires_at > datetime.utcnow()
            )
        )
        return result.scalars().all()

    @staticmethod
    async def update_session_activity(session_id: str, db: AsyncSession) -> None:
        """
        Update last activity timestamp

        Args:
            session_id: Session ID
            db: Database session
        """
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.last_activity = datetime.utcnow()
            await db.commit()

    @staticmethod
    async def update_socket_id(session_id: str, socket_id: str, db: AsyncSession) -> None:
        """
        Update socket ID for reconnection

        Args:
            session_id: Session ID
            socket_id: New socket ID
            db: Database session
        """
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.socket_id = socket_id
            session.last_activity = datetime.utcnow()
            await db.commit()

    @staticmethod
    async def delete_session(session_id: str, db: AsyncSession) -> None:
        """
        Delete a session

        Args:
            session_id: Session ID
            db: Database session
        """
        await db.execute(delete(Session).where(Session.id == session_id))
        await db.commit()

    @staticmethod
    async def delete_user_sessions(user_id: int, db: AsyncSession) -> None:
        """
        Delete all sessions for a user (logout from all devices)

        Args:
            user_id: User ID
            db: Database session
        """
        await db.execute(delete(Session).where(Session.user_id == user_id))
        await db.commit()

    @staticmethod
    async def cleanup_expired_sessions(db: AsyncSession) -> int:
        """
        Clean up expired sessions

        Args:
            db: Database session

        Returns:
            Number of deleted sessions
        """
        result = await db.execute(
            delete(Session).where(Session.expires_at <= datetime.utcnow())
        )
        await db.commit()
        return result.rowcount
