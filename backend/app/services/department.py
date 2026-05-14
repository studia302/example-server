from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Department
from app.db.models import Employee
from app.schemas.department import DeleteDepartmentMode
from app.schemas.department import DepartmentCreate
from app.schemas.department import DepartmentDetailsResponse
from app.schemas.department import DepartmentRead
from app.schemas.department import DepartmentTreeNode
from app.schemas.department import DepartmentUpdate
from app.schemas.employee import EmployeeCreate
from app.schemas.employee import EmployeeRead
from app.services.exceptions import ServiceError


class DepartmentService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_department(self, payload: DepartmentCreate) -> DepartmentRead:
        if payload.parent_id is not None:
            self._get_department_or_404(payload.parent_id)

        self._ensure_department_name_is_unique(payload.name, payload.parent_id)

        department = Department(name=payload.name, parent_id=payload.parent_id)
        self.session.add(department)
        self.session.commit()
        self.session.refresh(department)
        return DepartmentRead.model_validate(department)

    def create_employee(self, department_id: int, payload: EmployeeCreate) -> EmployeeRead:
        self._get_department_or_404(department_id)

        employee = Employee(
            department_id=department_id,
            full_name=payload.full_name,
            position=payload.position,
            hired_at=payload.hired_at,
        )
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return EmployeeRead.model_validate(employee)

    def get_department_details(
        self,
        department_id: int,
        depth: int,
        include_employees: bool,
    ) -> DepartmentDetailsResponse:
        department = self._get_department_or_404(department_id)
        employees = self._get_department_employees(department_id) if include_employees else []
        children = self._build_department_tree(department_id, depth)

        return DepartmentDetailsResponse(
            department=DepartmentRead.model_validate(department),
            employees=[EmployeeRead.model_validate(item) for item in employees],
            children=children,
        )

    def update_department(self, department_id: int, payload: DepartmentUpdate) -> DepartmentRead:
        department = self._get_department_or_404(department_id)
        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            return DepartmentRead.model_validate(department)

        new_name = update_data.get("name", department.name)
        new_parent_id = update_data.get("parent_id", department.parent_id)

        if new_parent_id == department_id:
            raise ServiceError(409, "Подразделение не может быть родителем самого себя.")

        if new_parent_id is not None:
            self._get_department_or_404(new_parent_id)
            self._ensure_no_cycle(department_id, new_parent_id)

        self._ensure_department_name_is_unique(
            name=new_name,
            parent_id=new_parent_id,
            exclude_department_id=department_id,
        )

        if "name" in update_data:
            department.name = new_name
        if "parent_id" in update_data:
            department.parent_id = new_parent_id

        self.session.commit()
        self.session.refresh(department)
        return DepartmentRead.model_validate(department)

    def delete_department(
        self,
        department_id: int,
        mode: DeleteDepartmentMode,
        reassign_to_department_id: int | None,
    ) -> None:
        department = self._get_department_or_404(department_id)

        if mode is DeleteDepartmentMode.CASCADE:
            self.session.delete(department)
            self.session.commit()
            return

        if reassign_to_department_id is None:
            raise ServiceError(
                400,
                "Параметр reassign_to_department_id обязателен при mode=reassign.",
            )

        if reassign_to_department_id == department_id:
            raise ServiceError(
                409,
                "Нельзя перевести сотрудников в удаляемое подразделение.",
            )

        self._get_department_or_404(reassign_to_department_id)

        employees = self.session.scalars(
            select(Employee).where(Employee.department_id == department_id)
        ).all()
        for employee in employees:
            employee.department_id = reassign_to_department_id

        children = self.session.scalars(
            select(Department).where(Department.parent_id == department_id)
        ).all()
        for child in children:
            child.parent_id = department.parent_id

        self.session.delete(department)
        self.session.commit()

    def _get_department_or_404(self, department_id: int) -> Department:
        department = self.session.get(Department, department_id)
        if department is None:
            raise ServiceError(404, "Подразделение не найдено.")
        return department

    def _ensure_department_name_is_unique(
        self,
        name: str,
        parent_id: int | None,
        exclude_department_id: int | None = None,
    ) -> None:
        stmt = select(Department).where(Department.name == name)
        if parent_id is None:
            stmt = stmt.where(Department.parent_id.is_(None))
        else:
            stmt = stmt.where(Department.parent_id == parent_id)

        if exclude_department_id is not None:
            stmt = stmt.where(Department.id != exclude_department_id)

        duplicate = self.session.scalar(stmt)
        if duplicate is not None:
            raise ServiceError(
                409,
                "Подразделение с таким названием уже существует в рамках выбранного родителя.",
            )

    def _ensure_no_cycle(self, department_id: int, new_parent_id: int) -> None:
        current_department_id = new_parent_id

        while current_department_id is not None:
            if current_department_id == department_id:
                raise ServiceError(
                    409,
                    "Нельзя переместить подразделение внутрь собственного поддерева.",
                )

            parent_id = self.session.scalar(
                select(Department.parent_id).where(Department.id == current_department_id)
            )
            current_department_id = parent_id

    def _get_department_employees(self, department_id: int) -> list[Employee]:
        return list(
            self.session.scalars(
                select(Employee)
                .where(Employee.department_id == department_id)
                .order_by(Employee.full_name.asc(), Employee.created_at.asc())
            )
        )

    def _build_department_tree(
        self,
        department_id: int,
        depth: int,
    ) -> list[DepartmentTreeNode]:
        if depth <= 0:
            return []

        children = list(
            self.session.scalars(
                select(Department)
                .where(Department.parent_id == department_id)
                .order_by(Department.name.asc(), Department.created_at.asc())
            )
        )

        return [
            DepartmentTreeNode(
                id=child.id,
                name=child.name,
                parent_id=child.parent_id,
                created_at=child.created_at,
                children=self._build_department_tree(child.id, depth - 1),
            )
            for child in children
        ]
