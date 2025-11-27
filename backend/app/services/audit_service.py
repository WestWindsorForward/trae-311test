import json
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import AuditEvent

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, actor_id: int, action: str, entity_type: str, entity_id: int, metadata: dict | None = None) -> AuditEvent:
        event = AuditEvent(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=json.dumps(metadata or {})
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event
