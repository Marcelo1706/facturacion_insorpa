from fastcrud import FastCRUD

from ..models.secuencia import Secuencia
from ..schemas.secuencia import SecuenciaCreate, SecuenciaDelete, SecuenciaUpdate, SecuenciaUpdateInternal

CRUDSecuencia = FastCRUD[
    Secuencia,
    SecuenciaCreate,
    SecuenciaUpdate,
    SecuenciaUpdateInternal,
    SecuenciaDelete
]
crud_secuencia = CRUDSecuencia(Secuencia)
