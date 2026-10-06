#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def base_fake_bin(root: Path, log: Path) -> Path:
    fake = root / "bin"
    fake.mkdir()

    write_executable(
        fake / "git",
        "#!/bin/sh\n"
        "echo \"git $*\" >> \"$CALL_LOG\"\n"
        "if [ \"$1\" = \"--version\" ]; then echo 'git version 2.50.0'; fi\n"
        "exit 0\n",
    )
    write_executable(
        fake / "node",
        "#!/bin/sh\n"
        "echo 'v20.0.0'\n",
    )
    write_executable(
        fake / "npm",
        "#!/bin/sh\n"
        "echo \"npm $*\" >> \"$CALL_LOG\"\n"
        "if [ \"$1\" = \"--version\" ]; then echo '10.0.0'; fi\n"
        "exit 0\n",
    )
    write_executable(
        fake / "python3",
        "#!/bin/sh\n"
        "if [ \"$1\" = \"--version\" ]; then echo 'Python 3.11.0'; exit 0; fi\n"
        "if [ \"$1\" = \"-c\" ]; then exit 0; fi\n"
        "exit 0\n",
    )
    write_executable(
        fake / "uipro",
        "#!/bin/sh\n"
        "echo \"uipro $*\" >> \"$CALL_LOG\"\n"
        "case \" $* \" in *' --dry-run '*) exit 88;; esac\n"
        "exit 0\n",
    )
    return fake


def run_bootstrap(fake: Path, log: Path, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = f"{fake}:/usr/bin:/bin"
    env["CALL_LOG"] = str(log)
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        ["bash", "scripts/bootstrap.sh", *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


with tempfile.TemporaryDirectory(prefix="multi-agents-bootstrap-") as tmp:
    tmp_root = Path(tmp)
    log = tmp_root / "calls.log"
    fake = base_fake_bin(tmp_root, log)

    # Gemini: list output is on stderr; rerun must detect installed extension
    # and must not call extensions install. uipro must never receive --dry-run.
    write_executable(
        fake / "gemini",
        "#!/bin/sh\n"
        "echo \"gemini $*\" >> \"$CALL_LOG\"\n"
        "if [ \"$1\" = \"--version\" ]; then echo '0.62.0'; exit 0; fi\n"
        "if [ \"$1 $2\" = \"extensions list\" ]; then echo 'superpowers 6.4.2' >&2; exit 0; fi\n"
        "if [ \"$1 $2\" = \"extensions install\" ]; then exit 77; fi\n"
        "exit 0\n",
    )

    result = run_bootstrap(fake, log, "--install", "gemini")
    if result.returncode != 0:
        print("[fail] Gemini idempotent bootstrap failed")
        print(result.stdout)
        raise SystemExit(1)

    calls = log.read_text(encoding="utf-8")
    if "gemini extensions install" in calls:
        raise SystemExit("[fail] Gemini rerun tried to reinstall Superpowers")
    if "--dry-run" in calls:
        raise SystemExit("[fail] bootstrap passed unsupported --dry-run to uipro")
    if "uipro init --ai gemini" not in calls:
        raise SystemExit("[fail] Gemini bootstrap did not reach uipro init")

    print("[ok] Gemini stderr-list idempotence and uipro invocation")

    # Codex: an old marketplace registered from a different source/ref should
    # warn and continue rather than abort or install ECC from the wrong source.
    log.write_text("", encoding="utf-8")
    write_executable(
        fake / "codex",
        "#!/bin/sh\n"
        "echo \"codex $*\" >> \"$CALL_LOG\"\n"
        "if [ \"$1\" = \"--version\" ]; then echo 'codex-cli 0.160.1'; exit 0; fi\n"
        "if [ \"$1 $2 $3\" = \"plugin marketplace add\" ]; then\n"
        "  echo 'already added from a different source' >&2\n"
        "  exit 1\n"
        "fi\n"
        "if [ \"$1 $2\" = \"plugin add\" ]; then exit 78; fi\n"
        "exit 0\n",
    )

    result = run_bootstrap(fake, log, "--install", "codex")
    if result.returncode != 0:
        print("[fail] Codex different-source marketplace handling failed")
        print(result.stdout)
        raise SystemExit(1)

    calls = log.read_text(encoding="utf-8")
    if "codex plugin add" in calls:
        raise SystemExit("[fail] Codex bootstrap installed ECC after marketplace source mismatch")
    if "--dry-run" in calls:
        raise SystemExit("[fail] bootstrap passed unsupported --dry-run to uipro")
    if "uipro init --ai codex" not in calls:
        raise SystemExit("[fail] Codex bootstrap did not continue to uipro init")

    print("[ok] Codex marketplace source mismatch is non-destructive")

print("Bootstrap regression tests passed.")
