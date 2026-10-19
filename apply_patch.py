"""Create a verified translated copy of the supported original disc dump."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Folder with the original 29 BIN tracks and CUE")
    parser.add_argument("output", type=Path, nargs="?", help="New output folder; must not already exist")
    parser.add_argument("--check", action="store_true", help="Verify the source without creating output")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    manifest = json.loads((here / "source-hashes.json").read_text(encoding="utf-8"))
    source = args.source.resolve()
    if not source.is_dir():
        parser.error("Source folder does not exist.")
    for row in manifest["tracks"]:
        path = source / row["file"]
        if not path.is_file() or path.stat().st_size != row["bytes"] or digest(path) != row["source_sha256"]:
            parser.error("Original track does not match the required dump: " + row["file"])
    cues = []
    for path in source.iterdir():
        if path.is_file() and path.suffix.lower() == ".cue":
            text = path.read_text(encoding="utf-8-sig")
            normalized = "\n".join(text.splitlines()) + "\n"
            if hashlib.sha256(normalized.encode("utf-8")).hexdigest() == manifest["normalized_cue_sha256"]:
                cues.append(normalized)
    if not cues:
        parser.error("No matching original CUE layout found. Keep the original filenames and CUE together.")
    cue = cues[0]
    if set(re.findall(r'FILE "([^"]+)"', cue)) != {row["file"] for row in manifest["tracks"]}:
        parser.error("CUE references do not match the required track set.")
    print("All 29 original track hashes and the CUE layout match.")
    if args.check:
        return
    if args.output is None:
        parser.error("Specify a new output folder, or use --check.")
    output = args.output.resolve()
    if output.exists() or not output.parent.is_dir():
        parser.error("Output must be a new folder whose parent already exists.")
    tool = shutil.which("xdelta3")
    if not tool:
        parser.error("xdelta3 was not found on PATH. Install xdelta3 first.")
    for row in manifest["tracks"]:
        if "patch" in row and digest(here / row["patch"]) != row["patch_sha256"]:
            parser.error("Patch checksum mismatch: " + row["patch"])
    with tempfile.TemporaryDirectory(prefix="xak-english-", dir=output.parent) as temporary:
        temporary = Path(temporary)
        disc = temporary / "disc"
        disc.mkdir()
        for row in manifest["tracks"]:
            original, target = source / row["file"], disc / row["file"]
            if "patch" in row:
                subprocess.run([tool, "-d", "-s", str(original), str(here / row["patch"]), str(target)], check=True)
            else:
                shutil.copyfile(original, target)
            if digest(target) != row["patched_sha256"]:
                raise RuntimeError("Patched output checksum mismatch: " + row["file"])
        (disc / "Xak.cue").write_text(cue, encoding="utf-8", newline="\n")
        if output.exists():
            raise RuntimeError("Output folder appeared during patching; refusing to replace it.")
        disc.rename(output)
    print("Verified translated disc created: " + str(output))
    print("Launch Xak.cue and keep all 29 BIN files beside it.")


if __name__ == "__main__":
    main()
