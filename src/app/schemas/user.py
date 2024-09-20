from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class UserBase(BaseModel):
    nit: Annotated[str, Field(min_length=14, max_length=14, examples=["00000000000000"])]


class User(TimestampSchema, UserBase, UUIDSchema, PersistentDeletion):
    hashed_password: str


class UserRead(BaseModel):
    id: int
    nit: Annotated[str, Field(min_length=14, max_length=14, examples=["00000000000000"])]


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")
    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class UserCreateInternal(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nit: Annotated[str, Field(min_length=14, max_length=14, examples=["00000000000000"])]


class UserUpdateInternal(UserUpdate):
    updated_at: datetime


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserRestoreDeleted(BaseModel):
    is_deleted: bool
