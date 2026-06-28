import json
from pathlib import Path
from os import getenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(getenv("ERAG_DATA_DIR", PROJECT_ROOT / "data"))
RBAC_DIR = DATA_DIR / "rbac"
ACCESS_POLICY_FILE = RBAC_DIR / "access_policies.json"

class MockRBACDatabase:
    """Mock external schema layer representing database storage of RBAC rules."""
    @staticmethod
    def load_policies() -> dict:
        try:
            return json.loads(Path(ACCESS_POLICY_FILE).read_text(encoding="utf-8"))
        except Exception:
            return {"roles": {}, "users": {}, "sensitivity_levels": ["public", "internal", "confidential", "restricted"]}
