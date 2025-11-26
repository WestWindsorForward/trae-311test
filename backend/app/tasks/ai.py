import os

def _heuristic(payload: dict) -> dict:
    text = (payload.get("description") or "").lower()
    category = "other"
    if any(w in text for w in ["pothole", "road", "street"]):
        category = "road_maintenance"
    elif any(w in text for w in ["light", "lamp"]):
        category = "street_lighting"
    sentiment = "neutral"
    if any(w in text for w in ["angry", "furious", "terrible"]):
        sentiment = "angry"
    priority = "medium"
    if any(w in text for w in ["urgent", "immediately", "danger"]):
        priority = "urgent"
    return {"category": category, "sentiment": sentiment, "priority": priority}

def triage(payload: dict) -> dict:
    project_id = os.getenv("VERTEX_PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    if not project_id:
        return _heuristic(payload)
    try:
        from google.cloud import aiplatform
        aiplatform.init(project=project_id, location=location)
        return _heuristic(payload)
    except Exception:
        return _heuristic(payload)
