import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shapely.geometry import shape, Point
from ..models.models import GeoBoundary

async def is_point_in_boundary(db: AsyncSession, latitude: Optional[float], longitude: Optional[float]) -> bool:
    if latitude is None or longitude is None:
        return True
    result = await db.execute(select(GeoBoundary).order_by(GeoBoundary.id.desc()))
    boundary = result.scalar_one_or_none()
    if not boundary:
        return True
    try:
        geom = shape(json.loads(boundary.geojson))
        return geom.contains(Point(longitude, latitude))
    except Exception:
        return True
