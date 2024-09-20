from fastcrud import FastCRUD

from ..models.dte import DTE
from ..schemas.dte import DTECreate, DTEDelete, DTEUpdate, DTEUpdateInternal

CRUDDTE = FastCRUD[
    DTE,
    DTECreate,
    DTEUpdate,
    DTEUpdateInternal,
    DTEDelete
]
crud_dte = CRUDDTE(DTE)
