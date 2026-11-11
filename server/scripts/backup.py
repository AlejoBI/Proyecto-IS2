"""Create and prune MongoDB/Chroma backups using deployment tooling."""

import argparse
import subprocess
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from server.app.configurations import Settings


def create_backup(settings: Settings) -> Path:
    destination = Path(settings.BACKUP_DIR)
    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = destination / stamp
    backup_dir.mkdir()
    mongo_dir = backup_dir / "mongodb"
    subprocess.run([
        "mongodump", f"--uri={settings.MONGODB_URI}",
        f"--db={settings.MONGODB_DATABASE}", f"--out={mongo_dir}",
    ], check=True)
    chroma_archive = backup_dir / "chroma_data.tar.gz"
    with tarfile.open(chroma_archive, "w:gz") as archive:
        archive.add(settings.CHROMA_PATH, arcname="chroma_data")
    return backup_dir


def prune_backups(settings: Settings) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.BACKUP_RETENTION_DAYS)
    for path in Path(settings.BACKUP_DIR).iterdir():
        if not path.is_dir():
            continue
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        if modified < cutoff:
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            path.rmdir()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prune-only", action="store_true")
    args = parser.parse_args()
    settings = Settings()
    if not args.prune_only:
        print(f"Created backup at {create_backup(settings)}")
    prune_backups(settings)
