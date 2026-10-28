#!/usr/bin/env python3
"""Combine Future Remote's Intel and Apple Silicon macOS app bundles."""
from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HOST = b"future-remote.duckdns.org"
PUBLIC_KEY = b"NgQBktnunnDC45ZaFZX9w1fixGsGD8Wb9J0WB94niB8="

def run(args: list[str], *, capture: bool = False) -> str:
    result = subprocess.run(args, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else ""

def inventory(root: Path) -> tuple[set[str], set[str]]:
    files: set[str] = set()
    links: set[str] = set()
    for current, dirs, names in os.walk(root, followlinks=False):
        base = Path(current)
        for name in list(dirs):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                links.add(rel)
                dirs.remove(name)
        for name in names:
            path = base / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                links.add(rel)
            elif path.is_file():
                files.add(rel)
    return files, links

def lipo_arches(path: Path) -> set[str] | None:
    result = subprocess.run(["lipo", "-archs", str(path)], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if result.returncode:
        return None
    return set(result.stdout.split())

def merge(intel: Path, arm: Path, output: Path) -> int:
    if not intel.is_dir() or not arm.is_dir():
        raise SystemExit("Expected both Future Remote.app architecture bundles.")
    intel_files, intel_links = inventory(intel)
    arm_files, arm_links = inventory(arm)
    if intel_files != arm_files:
        missing_arm = sorted(intel_files - arm_files)
        missing_intel = sorted(arm_files - intel_files)
        raise SystemExit(f"App bundle file layouts differ; missing from ARM={missing_arm}, missing from Intel={missing_intel}")
    if intel_links != arm_links:
        raise SystemExit("App bundle symlink layouts differ between Intel and Apple Silicon builds.")
    shutil.copytree(arm, output, symlinks=True)
    binaries: list[str] = []
    for rel in sorted(intel_files):
        intel_file, arm_file = intel / rel, arm / rel
        intel_arches, arm_arches = lipo_arches(intel_file), lipo_arches(arm_file)
        if intel_arches is None and arm_arches is None:
            continue
        if intel_arches is None or arm_arches is None:
            raise SystemExit(f"Mach-O mismatch between architecture builds: {rel}")
        if "x86_64" not in intel_arches or "arm64" not in arm_arches:
            raise SystemExit(f"Wrong architecture slices for {rel}: Intel={sorted(intel_arches)}, ARM={sorted(arm_arches)}")
        destination = output / rel
        with tempfile.TemporaryDirectory(dir=destination.parent) as temp_dir:
            temp = Path(temp_dir)
            intel_thin, arm_thin, universal = temp / "intel", temp / "arm", temp / "universal"
            run(["lipo", str(intel_file), "-thin", "x86_64", "-output", str(intel_thin)])
            run(["lipo", str(arm_file), "-thin", "arm64", "-output", str(arm_thin)])
            run(["lipo", "-create", str(intel_thin), str(arm_thin), "-output", str(universal)])
            os.chmod(universal, intel_file.stat().st_mode & 0o777)
            os.replace(universal, destination)
        merged_arches = lipo_arches(destination) or set()
        if not {"x86_64", "arm64"}.issubset(merged_arches):
            raise SystemExit(f"Universal merge verification failed for {rel}: {sorted(merged_arches)}")
        binaries.append(rel)
    if not binaries:
        raise SystemExit("No Mach-O binaries were found in the macOS app bundle.")
    # lipo invalidates the old code signatures; a later CI step signs the complete bundle again.
    for signature in sorted(output.rglob("_CodeSignature"), key=lambda p: len(p.parts), reverse=True):
        if signature.is_dir():
            shutil.rmtree(signature, ignore_errors=True)
    for sealed in output.rglob("CodeResources"):
        if sealed.is_file() or sealed.is_symlink():
            sealed.unlink(missing_ok=True)
    info_path = output / "Contents/Info.plist"
    with info_path.open("rb") as stream:
        metadata = plistlib.load(stream)
    if metadata.get("CFBundleName") != "Future Remote" or metadata.get("CFBundleDisplayName") != "Future Remote":
        raise SystemExit("Future Remote display-name metadata is missing from the universal app.")
    executable = output / "Contents/MacOS" / metadata.get("CFBundleExecutable", "RustDesk")
    executable_arches = lipo_arches(executable) if executable.is_file() else None
    if not executable_arches or not {"x86_64", "arm64"}.issubset(executable_arches):
        raise SystemExit("The Future Remote app executable is not universal.")
    haystack = b"".join(path.read_bytes() for rel in binaries for path in [output / rel])
    for label, needle in (("server hostname", HOST), ("public key", PUBLIC_KEY)):
        if needle not in haystack and needle.decode("ascii").encode("utf-16le") not in haystack:
            raise SystemExit(f"Future Remote universal binary is missing the configured {label}.")
    icon = output / "Contents/Resources/AppIcon.icns"
    if not icon.is_file() or icon.stat().st_size == 0:
        raise SystemExit("Future Soluções app icon is missing from the universal app.")
    print(f"Validated Future Remote universal app: {len(binaries)} Mach-O files contain x86_64 and arm64 slices.")
    print("Validated Future Remote display name, configured server, public key and app icon.")
    return len(binaries)

def main() -> int:
    if len(sys.argv) != 4:
        print(f"Usage: {Path(sys.argv[0]).name} INTEL.app ARM.app OUTPUT.app", file=sys.stderr)
        return 2
    merge(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())