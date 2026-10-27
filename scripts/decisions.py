#!/usr/bin/env python3
"""Safely initialise and maintain a project-local decisions.md ledger."""

import argparse
import fcntl
import os
import re
import stat
import sys
import tempfile
from pathlib import Path


HEADER = "# Project decisions\n\n## Ledger\n"
ENTRY = re.compile(
    r"^- (D-\d{4,}) \| (active|superseded) \| "
    r"(decision|rejection|constraint|correction) \| (.+?) \| because (.+)$"
)
SUPERSEDED_BY = re.compile(r" \| superseded by (D-\d{4,})$")
CONFLICT_MARKER = re.compile(r"^(<<<<<<<|=======|>>>>>>>)", re.MULTILINE)


def root_and_ledger(root_arg):
    root = Path(root_arg).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")
    ledger = root / "decisions.md"
    if ledger.is_symlink():
        raise ValueError(f"Refusing to follow a decisions.md symlink: {ledger}")
    return root, ledger


def locked(root):
    """Lock the directory so cooperating CLI processes serialize mutations."""
    descriptor = os.open(root, os.O_RDONLY)
    fcntl.flock(descriptor, fcntl.LOCK_EX)
    return descriptor


def unlock(descriptor):
    fcntl.flock(descriptor, fcntl.LOCK_UN)
    os.close(descriptor)


def parse(content, path):
    if CONFLICT_MARKER.search(content):
        raise ValueError("Merge conflict markers found; resolve manually")
    lines = content.splitlines()
    records = []
    for number, line in enumerate(lines, 1):
        if not line.startswith("- D-"):
            continue
        match = ENTRY.fullmatch(line)
        if not match:
            raise ValueError(f"Malformed decision entry at line {number}")
        identifier, status, category, statement, detail = match.groups()
        replacement = None
        superseded = SUPERSEDED_BY.search(detail)
        if superseded:
            replacement = superseded.group(1)
            detail = detail[:superseded.start()]
        if not detail.strip():
            raise ValueError(f"Missing rationale at line {number}")
        records.append({
            "id": identifier,
            "status": status,
            "category": category,
            "statement": statement,
            "detail": detail,
            "replacement": replacement,
            "line": number,
        })

    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate decision IDs")
    by_id = {record["id"]: record for record in records}
    for record in records:
        replacement = record["replacement"]
        if record["status"] == "superseded":
            if not replacement or replacement not in by_id:
                raise ValueError(f"{record['id']} is superseded without a valid replacement reference")
        elif replacement:
            raise ValueError(f"Active entry {record['id']} has a superseded-by reference")

    for record in records:
        seen = set()
        current = record
        while current["replacement"]:
            if current["id"] in seen:
                raise ValueError(f"Supersession cycle includes {current['id']}")
            seen.add(current["id"])
            current = by_id[current["replacement"]]
        if current["status"] != "active":
            raise ValueError(f"Supersession chain from {record['id']} does not end at an active entry")

    active_keys = {}
    for record in records:
        if record["status"] != "active":
            continue
        key = (record["category"], " ".join(record["statement"].casefold().split()))
        if key in active_keys:
            raise ValueError(
                f"Duplicate active statement in {record['id']} and {active_keys[key]}"
            )
        active_keys[key] = record["id"]

    if not any(line.strip() == "## Ledger" for line in lines):
        raise ValueError("Missing ledger heading")
    if not path.exists():
        raise ValueError(f"No decisions.md exists: {path}")
    return lines, records


def read_ledger(path):
    if not path.exists():
        raise ValueError("No decisions.md exists; run init first")
    return parse(path.read_text(encoding="utf-8"), path)


def clean(value, label):
    value = " ".join(value.split())
    if not value:
        raise ValueError(f"{label} must not be empty")
    if "|" in value:
        raise ValueError(f"{label} must not contain | (the ledger uses it as a field separator)")
    return value


def write_atomically(path, content):
    descriptor, temp_name = tempfile.mkstemp(prefix=".decisions-", dir=path.parent)
    try:
        if path.exists():
            os.fchmod(descriptor, stat.S_IMODE(path.stat().st_mode))
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("init", "add", "supersede", "validate"):
        command = sub.add_parser(action)
        command.add_argument("--root", required=True, help="Project directory containing decisions.md")
        if action == "add":
            command.add_argument("--category", required=True,
                                 choices=["decision", "rejection", "constraint", "correction"])
            command.add_argument("--decision", required=True, help="Settled statement to record")
            command.add_argument("--why", default="reason not provided")
            command.add_argument("--rejected", help="Rejected alternative and why")
        elif action == "supersede":
            command.add_argument("--id", required=True, help="Active entry being replaced")
            command.add_argument("--by", required=True, help="Existing active replacement entry")

    args = parser.parse_args()
    root = ledger = lock_fd = None
    try:
        root, ledger = root_and_ledger(args.root)
        lock_fd = locked(root)
        if args.action == "init":
            if ledger.exists():
                read_ledger(ledger)
                print(f"Already exists (unchanged): {ledger}")
            else:
                write_atomically(ledger, HEADER)
                print(f"Created: {ledger}")
            return

        lines, records = read_ledger(ledger)
        if args.action == "validate":
            print(f"Valid structure and references: {len(records)} entries in {ledger}")
            print("Note: semantic conflicts still require human review.")
            return

        by_id = {record["id"]: record for record in records}
        if args.action == "add":
            identifier_number = max((int(record["id"][2:]) for record in records), default=0) + 1
            identifier = f"D-{identifier_number:04d}"
            statement = clean(args.decision, "Decision")
            why = clean(args.why, "Rationale")
            rejected = clean(args.rejected, "Rejected alternative") if args.rejected else None
            detail = f"because {why}"
            if rejected:
                detail += f" | rejected {rejected}"
            line = f"- {identifier} | active | {args.category} | {statement} | {detail}"
            updated = "\n".join(lines)
            if updated and not updated.endswith("\n"):
                updated += "\n"
            updated += line + "\n"
            parse(updated, ledger)
            write_atomically(ledger, updated)
            print(f"Added {identifier}: {ledger}")
            return

        if args.id == args.by or args.id not in by_id or args.by not in by_id:
            raise ValueError("Both distinct existing IDs are required")
        old = by_id[args.id]
        new = by_id[args.by]
        if old["status"] != "active":
            raise ValueError(f"Target entry {args.id} is not active")
        if new["status"] != "active":
            raise ValueError(f"Replacement entry {args.by} is not active")
        old_line = lines[old["line"] - 1]
        lines[old["line"] - 1] = old_line.replace(" | active | ", " | superseded | ", 1)
        lines[old["line"] - 1] += f" | superseded by {args.by}"
        updated = "\n".join(lines) + "\n"
        parse(updated, ledger)
        write_atomically(ledger, updated)
        print(f"Superseded {args.id} by {args.by}: {ledger}")
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    finally:
        if lock_fd is not None:
            unlock(lock_fd)


if __name__ == "__main__":
    main()
