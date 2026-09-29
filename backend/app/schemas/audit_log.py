from app.core.enums import AuditAction, AuditModule, Role
from app.schemas.common import CamelModel, DocModel, ObjectIdStr, UtcDatetime


class AuditActor(CamelModel):
    id: ObjectIdStr
    name: str
    role: Role


class AuditLogOut(DocModel):
    user: AuditActor
    action: AuditAction
    module: AuditModule
    reference_id: ObjectIdStr | None = None
    description: str
    ip: str | None = None
    created_at: UtcDatetime
