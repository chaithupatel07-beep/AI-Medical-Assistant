"""User activity logging helper."""

import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.entities import UserActivity


def log_activity(
    db: Session,
    *,
    user_id: str,
    activity_type: str,
    description: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> UserActivity:
    entry = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        description=description[:500],
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata) if metadata is not None else None,
    )
    db.add(entry)
    return entry
