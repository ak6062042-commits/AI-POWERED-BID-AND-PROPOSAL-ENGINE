
import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional

WORKSPACES_DIR = os.path.join(os.path.dirname(__file__), "data", "workspaces")
os.makedirs(WORKSPACES_DIR, exist_ok=True)


def _path(workspace_id: str) -> str:
    return os.path.join(WORKSPACES_DIR, f"{workspace_id}.json")


def create_workspace(name: str) -> Dict[str, Any]:
    workspace_id = uuid.uuid4().hex[:10]
    record = {
        "id": workspace_id,
        "name": name,
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "status": "new",  
        "source_file": None,
        "extraction": None,
        "checklist": None,
        "checklist_summary": None,
        "draft": None,
        "scoring_inputs": None,
        "scoring_result": None,
        "go_no_go": None,
    }
    save_workspace(record)
    return record


def save_workspace(record: Dict[str, Any]) -> None:
    with open(_path(record["id"]), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)


def get_workspace(workspace_id: str) -> Optional[Dict[str, Any]]:
    p = _path(workspace_id)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def list_workspaces() -> List[Dict[str, Any]]:
    records = []
    for fname in sorted(os.listdir(WORKSPACES_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(WORKSPACES_DIR, fname), encoding="utf-8") as f:
                record = json.load(f)
            records.append({
                "id": record["id"],
                "name": record["name"],
                "created_at": record["created_at"],
                "status": record["status"],
                "go_no_go": (record.get("go_no_go") or {}).get("decision"),
                "win_probability_pct": (record.get("scoring_result") or {}).get("win_probability_pct"),
            })
    records.sort(key=lambda r: r["created_at"], reverse=True)
    return records


def delete_workspace(workspace_id: str) -> bool:
    p = _path(workspace_id)
    if os.path.exists(p):
        os.remove(p)
        return True
    return False
