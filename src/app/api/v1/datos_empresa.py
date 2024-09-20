from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_datos_empresa import crud_datos_empresa
from ...schemas.datos_empresa import DatosEmpresaCreate, DatosEmpresaRead, DatosEmpresaUpdate

router = APIRouter(tags=["datos_empresa"])


@router.get(
    "/datos_empresa",
    response_model=PaginatedListResponse[DatosEmpresaRead],
    dependencies=[Depends(get_current_user)])
async def read_datos_empresa(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    datos_empresa_data = await crud_datos_empresa.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=DatosEmpresaRead
    )

    response: dict[str, Any] = paginated_response(crud_data=datos_empresa_data, page=page, items_per_page=items_per_page)
    return response


@router.post(
    "/datos_empresa",
    response_model=DatosEmpresaRead,
    status_code=201,
    dependencies=[Depends(get_current_user)])
async def write_datos_empresa(
    request: Request, datos_empresa: DatosEmpresaCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> DatosEmpresaRead:
    datos_empresa_row = await crud_datos_empresa.exists(db=db, nit=datos_empresa.nit)
    if datos_empresa_row:
        raise DuplicateValueException("NIT is already registered")

    created_datos_empresa: DatosEmpresaRead = await crud_datos_empresa.create(db=db, object=datos_empresa)
    return created_datos_empresa


@router.put(
    "/datos_empresa/{nit}",
    dependencies=[Depends(get_current_user)])
async def update_datos_empresa(
    request: Request, nit: str, datos_empresa: DatosEmpresaUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> DatosEmpresaRead:
    db_datos_empresa: DatosEmpresaRead | None = await crud_datos_empresa.get(
        db=db, schema_to_select=DatosEmpresaRead, nit=nit
    )
    if db_datos_empresa is None:
        raise NotFoundException("Datos Empresa not found")

    await crud_datos_empresa.update(db=db, object=datos_empresa, nit=nit)
    return {"message":"Datos Empresa updated successfully"}
