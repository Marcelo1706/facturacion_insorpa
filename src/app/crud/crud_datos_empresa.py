from fastcrud import FastCRUD

from ..models.datos_empresa import DatosEmpresa
from ..schemas.datos_empresa import (
    DatosEmpresaCreate,
    DatosEmpresaDelete,
    DatosEmpresaUpdate,
    DatosEmpresaUpdateInternal,
)

CRUDDatosEmpresa = FastCRUD[
    DatosEmpresa,
    DatosEmpresaCreate,
    DatosEmpresaUpdate,
    DatosEmpresaUpdateInternal,
    DatosEmpresaDelete
]
crud_datos_empresa = CRUDDatosEmpresa(DatosEmpresa)
