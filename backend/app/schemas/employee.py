from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import StringConstraints

PersonText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


class EmployeeCreate(BaseModel):
    full_name: PersonText = Field(
        ...,
        description="Полное имя сотрудника.",
        examples=["Ivan Petrov"],
    )
    position: PersonText = Field(
        ...,
        description="Должность сотрудника.",
        examples=["Backend Developer"],
    )
    hired_at: date | None = Field(
        default=None,
        description="Дата найма.",
        examples=["2024-09-01"],
    )


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор сотрудника.", examples=[101])
    department_id: int = Field(description="Идентификатор подразделения.", examples=[10])
    full_name: str = Field(description="Полное имя сотрудника.", examples=["Ivan Petrov"])
    position: str = Field(description="Должность сотрудника.", examples=["Backend Developer"])
    hired_at: date | None = Field(
        description="Дата найма.",
        examples=["2024-09-01"],
    )
    created_at: datetime = Field(
        description="Дата и время создания записи о сотруднике.",
        examples=["2026-05-14T10:15:00Z"],
    )
