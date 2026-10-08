#!/usr/bin/env python3
"""
Agent Skills Validator

Validates SKILL.md files against the Agent Skills specification:
- Frontmatter contains only name, description, license (optional)
- name: max 64 chars, lowercase alphanumeric + hyphens, no leading/trailing hyphen
- description: 1-1024 chars, non-empty
- license: optional string
- Body length: must not exceed 200 lines (excluding frontmatter)

Usage:
    python scripts/validate.py ./recon/SKILL.md
    python scripts/validate.py ./preflight/SKILL.md
    python scripts/validate.py ./hold/SKILL.md
    python scripts/validate.py ./ --all  # validate all SKILL.md files recursively

Exit codes:
    0: All validations passed
    1: One or more validation failures
"""

import sys
import re
import os
from pathlib import Path
from typing import Any
import yaml


ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license"}
MAX_LINE_COUNT = 200
DEFAULT_DIRS = ["recon", "preflight", "hold", "scope", "budget"]


def parse_frontmatter(content: str) -> tuple[list, str]:
    """Parse YAML frontmatter from Markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_yaml = parts[1]
    body = parts[2]

    try:
        frontmatter = yaml.safe_load(frontmatter_yaml) or {}
    except yaml.YAMLError as e:
        return None, f"Invalid YAML in frontmatter: {e}"

    return frontmatter, body


def validate_name(name: str, filepath: str) -> list[str]:
    """Validate name field against spec."""
    errors = []

    if not isinstance(name, str):
        errors.append(f"name must be a string, got {type(name).__name__}")
        return errors

    if len(name) > 64:
        errors.append(f"name exceeds 64 characters ({len(name)} chars)")

    if len(name) < 1:
        errors.append("name cannot be empty")
        return errors

    # Must match: lowercase letters, numbers, hyphens only
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
        errors.append(
            "name must use only lowercase letters, numbers, and hyphens; "
            "must not start or end with hyphen"
        )

    # Must not contain consecutive hyphens
    if "--" in name:
        errors.append("name cannot contain consecutive hyphens (--)")

    return errors


def validate_description(description: str, filepath: str) -> list[str]:
    """Validate description field against spec."""
    errors = []

    if not isinstance(description, str):
        errors.append(f"description must be a string, got {type(description).__name__}")
        return errors

    if len(description) < 1:
        errors.append("description cannot be empty")
        return errors

    if len(description) > 1024:
        errors.append(f"description exceeds 1024 characters ({len(description)} chars)")

    return errors


def validate_license(license_val: Any, filepath: str) -> list[str]:
    """Validate license field (optional)."""
    errors = []

    if license_val is None:
        return errors  # Optional field

    if not isinstance(license_val, str):
        errors.append(f"license must be a string, got {type(license_val).__name__}")

    return errors


def validate_name_directory_match(name: str, filepath: str) -> list[str]:
    """Validate that name matches parent directory name."""
    errors = []

    path = Path(filepath)
    dir_name = path.parent.name

    if name != dir_name:
        errors.append(
            f"name '{name}' does not match directory '{dir_name}'"
        )

    return errors


def validate_code_fences(body: str, filepath: str) -> list[str]:
    """Validate that markdown code fences are balanced.

    Counts lines that start with ``` (three backticks, optionally followed by language).
    The count must be even - each opening fence needs a closing fence.
    """
    errors = []

    fence_count = 0
    for line in body.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            fence_count += 1

    if fence_count % 2 == 1:
        errors.append(
            f"Unbalanced code fences: {fence_count} backtick-only lines found "
            f"(must be even)"
        )

    return errors


def validate_body_length(body: str, filepath: str) -> list[str]:
    """Validate body line count."""
    errors = []

    lines = body.strip().split("\n") if body.strip() else []
    line_count = len(lines)

    if line_count > MAX_LINE_COUNT:
        errors.append(
            f"body exceeds {MAX_LINE_COUNT} lines ({line_count} lines found)\n"
            f"Refactor to referenced files in references/ directory"
        )

    return errors


def validate_file(filepath: str) -> tuple[bool, list[str]]:
    """Validate a single SKILL.md file.

    Args:
        filepath: Path to SKILL.md file

    Returns:
        Tuple of (passed: bool, errors: list[str])
    """
    path = Path(filepath)

    if not path.exists():
        return False, [f"File does not exist: {filepath}"]

    if path.name != "SKILL.md":
        return False, [f"File must be named SKILL.md, got {path.name}"]

    content = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    errors = []

    if frontmatter is None:
        return False, ["Failed to parse frontmatter"]

    # Check for extra keys in frontmatter
    extra_keys = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if extra_keys:
        errors.append(
            f"Frontmatter contains disallowed keys: {', '.join(sorted(extra_keys))}\n"
            f"Allowed keys are: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        )

    # Validate required fields
    if "name" not in frontmatter:
        errors.append("Frontmatter missing required 'name' field")
    else:
        errors.extend(validate_name(frontmatter["name"], filepath))
        errors.extend(validate_name_directory_match(frontmatter["name"], filepath))

    if "description" not in frontmatter:
        errors.append("Frontmatter missing required 'description' field")
    else:
        errors.extend(validate_description(frontmatter["description"], filepath))

    if "license" in frontmatter:
        errors.extend(validate_license(frontmatter["license"], filepath))

    # Validate body length
    errors.extend(validate_body_length(body, filepath))

    # Validate code fence balance
    errors.extend(validate_code_fences(body, filepath))

    return len(errors) == 0, errors


def find_skill_files(path: str, recursive: bool = True) -> list[str]:
    """Find all SKILL.md files under given path."""
    path_obj = Path(path)

    if path_obj.is_file() and path_obj.name == "SKILL.md":
        return [str(path_obj)]

    if not path_obj.is_dir():
        return []

    pattern = "**/SKILL.md" if recursive else "SKILL.md"
    return [str(p) for p in path_obj.glob(pattern)]


def main():
    """Main entry point."""
    parser_args = sys.argv[1:]

    # Fix 1: Default behavior walks recon/, preflight/, hold/ explicitly
    all_mode = "--all" in parser_args or "-a" in parser_args
    explicit_paths = [p for p in parser_args if p not in {"--all", "-a"}]

    if not explicit_paths:
        # Default: check all five skill directories
        explicit_paths = DEFAULT_DIRS.copy()

    total_passed = 0
    total_failed = 0

    for path_str in explicit_paths:
        path_obj = Path(path_str)

        # If user passed a direct SKILL.md file, validate it
        if path_obj.is_file() and path_obj.name == "SKILL.md":
            passed, errors = validate_file(str(path_obj))

            if passed:
                print(f"[OK] {path_obj}")
                total_passed += 1
            else:
                print(f"[FAIL] {path_obj}")
                for error in errors:
                    print(f"    - {error}")
                total_failed += 1
            continue

        # Otherwise treat as directory and look for SKILL.md inside
        skill_md = path_obj / "SKILL.md"

        if not skill_md.exists():
            print(f"[FAIL] {path_str}/SKILL.md not found")
            total_failed += 1
            continue

        passed, errors = validate_file(str(skill_md))

        if passed:
            print(f"[OK] {skill_md}")
            total_passed += 1
        else:
            print(f"[FAIL] {skill_md}")
            for error in errors:
                print(f"    - {error}")
            total_failed += 1

    print()

    # Dynamic success message with skill count
    num_skills = len(explicit_paths)
    if total_failed == 0:
        print(f"All {num_skills} skills valid.")
    else:
        print(f"Results: {total_passed} passed, {total_failed} failed")

    sys.exit(1 if total_failed > 0 else 0)


if __name__ == "__main__":
    main()
