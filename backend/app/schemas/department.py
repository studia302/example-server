from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import StringConstraints

DepartmentName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


class DeleteDepartmentMode(StrEnum):
    CASCADE = "cascade"
    REASSIGN = "reassign"


class DepartmentCreate(BaseModel):
    name: DepartmentName = Field(
        ...,
        description="Название подразделения. Должно быть уникальным в пределах одного родительского подразделения.",
        examples=["Backend"],
    )
    parent_id: int | None = Field(
        default=None,
        description="ID родительского подразделения. Используйте null для создания корневого подразделения.",
        examples=[1],
    )


class DepartmentUpdate(BaseModel):
    name: DepartmentName | None = Field(
        default=None,
        description="Новое название подразделения.",
        examples=["Platform"],
    )
    parent_id: int | None = Field(
        default=None,
        description="Новый ID родительского подразделения. Используйте null, чтобы переместить подразделение в корень дерева.",
        examples=[2],
    )


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор подразделения.", examples=[10])
    name: str = Field(description="Название подразделения.", examples=["Backend"])
    parent_id: int | None = Field(
        description="Идентификатор родительского подразделения. Null для корневых подразделений.",
        examples=[1],
    )
    created_at: datetime = Field(
        description="Дата и время создания подразделения.",
        examples=["2026-05-14T10:00:00Z"],
    )


class DepartmentTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор подразделения.", examples=[11])
    name: str = Field(description="Название подразделения.", examples=["Backend Core"])
    parent_id: int | None = Field(
        description="Идентификатор родительского подразделения. Null для корневых подразделений.",
        examples=[10],
    )
    created_at: datetime = Field(
        description="Дата и время создания подразделения.",
        examples=["2026-05-14T10:05:00Z"],
    )
    children: list["DepartmentTreeNode"] = Field(
        default_factory=list,
        description="Вложенные дочерние подразделения до запрошенной глубины.",
    )


class DepartmentDetailsResponse(BaseModel):
    department: DepartmentRead = Field(
        description="Детали запрошенного подразделения.",
    )
    employees: list["EmployeeRead"] = Field(
        default_factory=list,
        description="Сотрудники подразделения. Возвращаются, если include_employees=true.",
    )
    children: list[DepartmentTreeNode] = Field(
        default_factory=list,
        description="Вложенные дочерние подразделения до запрошенной глубины.",
    )


class DepartmentDetailsQuery(BaseModel):
    depth: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Глубина вложенности дочерних подразделений в ответе.",
        examples=[2],
    )
    include_employees: bool = Field(
        default=True,
        description="Нужно ли включать сотрудников подразделения в ответ.",
        examples=[True],
    )


class DepartmentDeleteQuery(BaseModel):
    mode: DeleteDepartmentMode = Field(
        description="Режим удаления: cascade удаляет всё поддерево, reassign сначала переводит сотрудников в другое подразделение.",
        examples=["cascade"],
    )
    reassign_to_department_id: int | None = Field(
        default=None,
        ge=1,
        description="ID подразделения, в которое нужно перевести сотрудников. Обязательно при mode=reassign.",
        examples=[3],
    )


from app.schemas.employee import EmployeeRead

DepartmentTreeNode.model_rebuild()
