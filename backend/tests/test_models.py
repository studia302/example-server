from __future__ import annotations

from sqlalchemy import ForeignKey

from app.db.models import Department
from app.db.models import Employee


def test_department_self_reference_uses_cascade_delete() -> None:
    parent_id_column = Department.__table__.c.parent_id
    foreign_key = next(iter(parent_id_column.foreign_keys))

    assert isinstance(foreign_key, ForeignKey)
    assert foreign_key.ondelete == "CASCADE"


def test_employee_department_fk_uses_cascade_delete() -> None:
    department_id_column = Employee.__table__.c.department_id
    foreign_key = next(iter(department_id_column.foreign_keys))

    assert isinstance(foreign_key, ForeignKey)
    assert foreign_key.ondelete == "CASCADE"
