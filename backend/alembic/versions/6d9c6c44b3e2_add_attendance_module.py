"""Add Attendance Module

Revision ID: 6d9c6c44b3e2
Revises: 3abef1e5ef82
Create Date: 2026-03-12 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d9c6c44b3e2'
down_revision: Union[str, Sequence[str], None] = '3abef1e5ef82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Employee Checkins ---
    op.create_table('hr_employee_checkins',
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('log_type', sa.String(), nullable=False),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('device_id', sa.String(), nullable=True),
        sa.Column('skip_auto_attendance', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('modified_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['hr_employees.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hr_employee_checkins_employee_id'), 'hr_employee_checkins', ['employee_id'], unique=False)
    op.create_index(op.f('ix_hr_employee_checkins_tenant_id'), 'hr_employee_checkins', ['tenant_id'], unique=False)
    
    # RLS for hr_employee_checkins
    op.execute("ALTER TABLE hr_employee_checkins ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY tenant_isolation ON hr_employee_checkins USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID)")

    # --- Attendance ---
    op.create_table('hr_attendance',
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('attendance_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('docstatus', sa.Integer(), nullable=False),
        sa.Column('working_hours', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('late_entry', sa.Boolean(), nullable=False),
        sa.Column('early_exit', sa.Boolean(), nullable=False),
        sa.Column('leave_application_id', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('modified_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hr_companies.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['employee_id'], ['hr_employees.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['leave_application_id'], ['hr_leave_applications.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'attendance_date', name='uq_employee_attendance_date')
    )
    op.create_index(op.f('ix_hr_attendance_company_id'), 'hr_attendance', ['company_id'], unique=False)
    op.create_index(op.f('ix_hr_attendance_employee_id'), 'hr_attendance', ['employee_id'], unique=False)
    op.create_index(op.f('ix_hr_attendance_tenant_id'), 'hr_attendance', ['tenant_id'], unique=False)

    # RLS for hr_attendance
    op.execute("ALTER TABLE hr_attendance ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY tenant_isolation ON hr_attendance USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID)")

    # --- Attendance Requests ---
    op.create_table('hr_attendance_requests',
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('docstatus', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('modified_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['hr_companies.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['employee_id'], ['hr_employees.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hr_attendance_requests_company_id'), 'hr_attendance_requests', ['company_id'], unique=False)
    op.create_index(op.f('ix_hr_attendance_requests_employee_id'), 'hr_attendance_requests', ['employee_id'], unique=False)
    op.create_index(op.f('ix_hr_attendance_requests_tenant_id'), 'hr_attendance_requests', ['tenant_id'], unique=False)

    # RLS for hr_attendance_requests
    op.execute("ALTER TABLE hr_attendance_requests ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY tenant_isolation ON hr_attendance_requests USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID)")


def downgrade() -> None:
    op.drop_index(op.f('ix_hr_attendance_requests_tenant_id'), table_name='hr_attendance_requests')
    op.drop_index(op.f('ix_hr_attendance_requests_employee_id'), table_name='hr_attendance_requests')
    op.drop_index(op.f('ix_hr_attendance_requests_company_id'), table_name='hr_attendance_requests')
    op.drop_table('hr_attendance_requests')
    
    op.drop_index(op.f('ix_hr_attendance_tenant_id'), table_name='hr_attendance')
    op.drop_index(op.f('ix_hr_attendance_employee_id'), table_name='hr_attendance')
    op.drop_index(op.f('ix_hr_attendance_company_id'), table_name='hr_attendance')
    op.drop_table('hr_attendance')
    
    op.drop_index(op.f('ix_hr_employee_checkins_tenant_id'), table_name='hr_employee_checkins')
    op.drop_index(op.f('ix_hr_employee_checkins_employee_id'), table_name='hr_employee_checkins')
    op.drop_table('hr_employee_checkins')
