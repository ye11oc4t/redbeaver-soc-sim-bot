from __future__ import annotations

import os
from pathlib import Path

from redbeaver.config import settings
from redbeaver.utils.eventlog import EventRecorder

NAME = "ransomware_marker"
DESCRIPTION = "Local FIM marker: create/overwrite/rename/delete only inside WORKDIR."

def run() -> str:
    rec = EventRecorder(NAME)
    scenario_dir = settings.workdir / NAME
    scenario_dir.mkdir(parents=True, exist_ok=True)
    rec.add("scenario_start", safe=True, destructive=False, scope=str(scenario_dir))

    files: list[Path] = []
    for i in range(25):
        p = scenario_dir / f"document_{i:02d}.txt"
        p.write_text(f"dummy record {i}\n" + "A" * 256, encoding="utf-8")
        files.append(p)
        rec.add("file_created", path=str(p))

    renamed: list[Path] = []
    for p in files:
        p.write_bytes(os.urandom(128))
        new_p = p.with_suffix(".locked.marker")
        p.rename(new_p)
        renamed.append(new_p)
        rec.add("file_overwrite_and_rename", old=str(p), new=str(new_p))

    note = scenario_dir / "README_REDBEAVER_SIMULATION.txt"
    note.write_text("This is a harmless ransomware simulation marker. No real files were encrypted.\n", encoding="utf-8")
    rec.add("ransom_note_marker_created", path=str(note))

    vss = scenario_dir / "windows_recovery_command_strings.log"
    vss.write_text(
        "vssadmin delete shadows /all /quiet [SIMULATION STRING ONLY]\n"
        "wbadmin delete catalog -quiet [SIMULATION STRING ONLY]\n",
        encoding="utf-8",
    )
    rec.add("recovery_deletion_string_marker", path=str(vss), executed=False)

    for p in renamed[:10]:
        p.unlink(missing_ok=True)
        rec.add("file_deleted", path=str(p))

    path = rec.save()
    return f"{NAME}: created=25 renamed=25 deleted=10 scope={scenario_dir}; events={path}"
