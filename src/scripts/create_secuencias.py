import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, String, Table, insert, select

from ..app.core.db.database import AsyncSession, async_engine, local_session
from ..app.models.secuencia import Secuencia

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_secuencias(session: AsyncSession) -> None:
    try:
        data = [
            {"tipo_dte": "01", "secuencia": 1},
            {"tipo_dte": "03", "secuencia": 1},
            {"tipo_dte": "04", "secuencia": 1},
            {"tipo_dte": "05", "secuencia": 1},
            {"tipo_dte": "06", "secuencia": 1},
            {"tipo_dte": "07", "secuencia": 1},
            {"tipo_dte": "08", "secuencia": 1},
            {"tipo_dte": "09", "secuencia": 1},
            {"tipo_dte": "11", "secuencia": 1},
            {"tipo_dte": "14", "secuencia": 1},
            {"tipo_dte": "15", "secuencia": 1},
        ]

        for record in data:
            query = select(Secuencia).filter_by(tipo_dte=record["tipo_dte"])
            result = await session.execute(query)
            secuencia = result.scalar_one_or_none()

            if secuencia is None:
                metadata = MetaData()
                secuencia_table = Table(
                    "secuencias",
                    metadata,
                    Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
                    Column("tipo_dte", String(255), nullable=False),
                    Column("secuencia", Integer, nullable=False),
                    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False),
                    Column("updated_at", DateTime),
                    Column("deleted_at", DateTime),
                    Column("is_deleted", Boolean, default=False, index=True),
                )

                stmt = insert(secuencia_table).values(record)
                async with async_engine.connect() as conn:
                    await conn.execute(stmt)
                    await conn.commit()

                logger.info(f"Secuencia {record['tipo_dte']} created successfully.")

            else:
                logger.info(f"Secuencia {record['tipo_dte']} already exists.")
    except Exception as e:
        logger.error(f"Error creating Secuencia: {e}")


async def main():
    async with local_session() as session:
        await create_secuencias(session)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
