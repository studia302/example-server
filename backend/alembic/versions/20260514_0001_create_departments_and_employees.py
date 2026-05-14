from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260514_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["departments.id"],
            name=op.f("fk_departments_parent_id_departments"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("btrim(name) <> ''", name=op.f("ck_departments_name_not_empty")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_departments")),
    )
    op.create_index(op.f("ix_departments_id"), "departments", ["id"], unique=False)
    op.create_index(
        "uq_departments_parent_scope_name",
        "departments",
        [sa.literal_column("coalesce(parent_id, 0)"), "name"],
        unique=True,
    )

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("position", sa.String(length=255), nullable=False),
        sa.Column("hired_at", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name=op.f("fk_employees_department_id_departments"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "btrim(full_name) <> ''",
            name=op.f("ck_employees_full_name_not_empty"),
        ),
        sa.CheckConstraint(
            "btrim(position) <> ''",
            name=op.f("ck_employees_position_not_empty"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_employees")),
    )
    op.create_index(op.f("ix_employees_department_id"), "employees", ["department_id"], unique=False)
    op.create_index(op.f("ix_employees_id"), "employees", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_employees_id"), table_name="employees")
    op.drop_index(op.f("ix_employees_department_id"), table_name="employees")
    op.drop_table("employees")
    op.drop_index("uq_departments_parent_scope_name", table_name="departments")
    op.drop_index(op.f("ix_departments_id"), table_name="departments")
    op.drop_table("departments")
