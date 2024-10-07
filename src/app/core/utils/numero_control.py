from sqlalchemy.ext.asyncio import AsyncSession

from ...crud.crud_secuencia import crud_secuencia
from ...schemas.secuencia import SecuenciaRead, SecuenciaUpdate


def generar_numero_control(
    correlativo: int,
    tipo_dte: str,
    sucursal: str = "001",
    punto_venta: str = "001") -> str:
    sucursal = str(int(sucursal)).zfill(3)
    punto_venta = str(int(punto_venta)).zfill(3)
    return f"DTE-{tipo_dte}-T{sucursal}P{punto_venta}-{str(correlativo).zfill(15)}"


async def update_numero_control(
    db: AsyncSession,
    tipo_dte: str,
) -> None:
    db_secuencia = await crud_secuencia.get(
        db=db,
        schema_to_select=SecuenciaRead,
        tipo_dte=tipo_dte
    )

    if db_secuencia is None:
        return

    await crud_secuencia.update(
        db=db,
        object=SecuenciaUpdate(
            tipo_dte=db_secuencia["tipo_dte"],
            secuencia=db_secuencia["secuencia"] + 1
        ),
        id=db_secuencia["id"]
    )
