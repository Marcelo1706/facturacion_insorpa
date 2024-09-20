from datetime import UTC, datetime
import asyncio
import logging

from sqlalchemy import Column, Integer, MetaData, String, Table, insert, select, Boolean, DateTime

from ..app.core.config import settings
from ..app.core.db.database import AsyncSession, async_engine, local_session
from ..app.core.security import get_password_hash
from ..app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_user(session: AsyncSession) -> None:
    try:
        nit = settings.ADMIN_NAME
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)

        query = select(User).filter_by(nit=nit)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            metadata = MetaData()
            user_table = Table(
                "user",
                metadata,
                Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
                Column("nit", String(14), nullable=False),
                Column("hashed_password", String, nullable=False),
                Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False),
                Column("updated_at", DateTime),
                Column("deleted_at", DateTime),
                Column("is_deleted", Boolean, default=False, index=True),
            )

            data = {
                "nit": nit,
                "hashed_password": hashed_password,
            }

            stmt = insert(user_table).values(data)
            async with async_engine.connect() as conn:
                await conn.execute(stmt)
                await conn.commit()

            logger.info(f"NIT user {nit} created successfully.")

        else:
            logger.info(f"NIT user {nit} already exists.")

    except Exception as e:
        logger.error(f"Error creating NIT user: {e}")


async def main():
    async with local_session() as session:
        await create_first_user(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
