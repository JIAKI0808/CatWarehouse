import json
from pathlib import Path
from datetime import datetime


def get_backup_dir() -> Path:
    backup_dir = Path(__file__).parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def create_backup(data: dict) -> str:
    backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.json"
    filepath = backup_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filename


def list_backups() -> list[dict]:
    backup_dir = get_backup_dir()
    backups = []
    for f in sorted(backup_dir.glob("backup_*.json"), reverse=True):
        backups.append({
            "filename": f.name,
            "size": f.stat().st_size,
            "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
        })
    return backups


def read_backup(filename: str) -> dict:
    backup_dir = get_backup_dir()
    filepath = backup_dir / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Backup {filename} not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
