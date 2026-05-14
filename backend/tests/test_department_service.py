from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Department
from app.schemas.department import DepartmentCreate
from app.schemas.department import DepartmentUpdate
from app.services.department import DepartmentService
from app.services.exceptions import ServiceError


def make_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_factory()


def test_create_department_rejects_duplicate_name_within_same_parent() -> None:
    session = make_session()
    service = DepartmentService(session)

    root = service.create_department(DepartmentCreate(name="Engineering", parent_id=None))

    service.create_department(DepartmentCreate(name="Backend", parent_id=root.id))

    try:
        service.create_department(DepartmentCreate(name="Backend", parent_id=root.id))
    except ServiceError as exc:
        assert exc.status_code == 409
        assert "уже существует" in exc.detail
    else:
        raise AssertionError("Expected duplicate department name to raise ServiceError.")


def test_update_department_rejects_cycle() -> None:
    session = make_session()
    service = DepartmentService(session)

    root = Department(name="Engineering")
    child = Department(name="Backend", parent=root)
    grandchild = Department(name="Platform", parent=child)
    session.add_all([root, child, grandchild])
    session.commit()

    try:
        service.update_department(
            department_id=root.id,
            payload=DepartmentUpdate(parent_id=grandchild.id),
        )
    except ServiceError as exc:
        assert exc.status_code == 409
        assert "поддерева" in exc.detail
    else:
        raise AssertionError("Expected cycle detection to raise ServiceError.")
