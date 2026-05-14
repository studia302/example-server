from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Response
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.department import DeleteDepartmentMode
from app.schemas.department import DepartmentCreate
from app.schemas.department import DepartmentDetailsResponse
from app.schemas.department import DepartmentRead
from app.schemas.department import DepartmentUpdate
from app.schemas.employee import EmployeeCreate
from app.schemas.employee import EmployeeRead
from app.services.department import DepartmentService

router = APIRouter(prefix="/departments", tags=["departments"])


def get_department_service(
    session: Session = Depends(get_db_session),
) -> DepartmentService:
    return DepartmentService(session)


@router.post(
    "/",
    response_model=DepartmentRead,
    status_code=201,
    summary="Создать подразделение",
)
def create_department(
    payload: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentRead:
    return service.create_department(payload)


@router.post(
    "/{department_id}/employees/",
    response_model=EmployeeRead,
    status_code=201,
    summary="Создать сотрудника в подразделении",
)
def create_employee(
    department_id: int,
    payload: EmployeeCreate,
    service: DepartmentService = Depends(get_department_service),
) -> EmployeeRead:
    return service.create_employee(department_id, payload)


@router.get(
    "/{department_id}",
    response_model=DepartmentDetailsResponse,
    summary="Получить подразделение с сотрудниками и поддеревом",
)
def get_department_details(
    department_id: int,
    depth: Annotated[
        int,
        Query(ge=1, le=5, description="Глубина вложенности дочерних подразделений."),
    ] = 1,
    include_employees: Annotated[
        bool,
        Query(description="Нужно ли включать сотрудников подразделения в ответ."),
    ] = True,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentDetailsResponse:
    return service.get_department_details(
        department_id=department_id,
        depth=depth,
        include_employees=include_employees,
    )


@router.patch(
    "/{department_id}",
    response_model=DepartmentRead,
    summary="Обновить подразделение",
)
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentRead:
    return service.update_department(department_id, payload)


@router.delete(
    "/{department_id}",
    status_code=204,
    summary="Удалить подразделение",
)
def delete_department(
    department_id: int,
    mode: Annotated[
        DeleteDepartmentMode,
        Query(description="Режим удаления подразделения."),
    ],
    reassign_to_department_id: Annotated[
        int | None,
        Query(
            description="ID подразделения для перевода сотрудников. Обязательно при mode=reassign.",
            ge=1,
        ),
    ] = None,
    service: DepartmentService = Depends(get_department_service),
) -> Response:
    service.delete_department(
        department_id=department_id,
        mode=mode,
        reassign_to_department_id=reassign_to_department_id,
    )
    return Response(status_code=204)
