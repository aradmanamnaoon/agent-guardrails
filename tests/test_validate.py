"""Tests for the agent skills validator."""

import sys
from pathlib import Path
import tempfile
import pytest

# Import from scripts/validate.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from validate import validate_file, parse_frontmatter, DEFAULT_DIRS


class TestFrontmatterParsing:
    """Tests for parse_frontmatter function."""

    def test_frontmatter_parses_valid_input(self):
        """Test that valid YAML frontmatter is parsed correctly."""
        content = "---\nname: recon\ndescription: Research and plan.\nlicense: MIT\n---\nBody text here."
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {
            "name": "recon",
            "description": "Research and plan.",
            "license": "MIT"
        }
        assert body.strip() == "Body text here."

    def test_frontmatter_missing_opening_delimiter(self):
        """Test that missing opening delimiter doesn't crash."""
        content = "no frontmatter here"
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert body == "no frontmatter here"

    def test_frontmatter_unclosed(self):
        """Test that unclosed frontmatter doesn't raise."""
        content = "---\nname: recon\ndescription: test\n"  # No closing ---
        frontmatter, body = parse_frontmatter(content)

        # Should return something sane without raising
        assert isinstance(frontmatter, dict) or frontmatter is None


class TestValidation:
    """Tests for validate_file function using temp directories."""

    def test_unknown_frontmatter_key(self):
        """Test that unknown keys in frontmatter cause validation failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "recon"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"

            content = """---
name: recon
description: Test skill
version: 1.0
---
Body text."""

            skill_md.write_text(content, encoding="utf-8")

            passed, errors = validate_file(str(skill_md))

            assert passed is False
            error_str = "\n".join(errors)
            assert "version" in error_str

    def test_name_mismatch_with_directory(self):
        """Test that name field must match directory name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "recon"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"

            content = """---
name: preflight
description: This should fail
---
Body text."""

            skill_md.write_text(content, encoding="utf-8")

            passed, errors = validate_file(str(skill_md))

            assert passed is False
            error_str = "\n".join(errors)
            assert "does not match" in error_str

    def test_description_too_long(self):
        """Test that description over 1024 chars fails validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "recon"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"

            long_desc = "x" * 1100

            content = f"""---
name: recon
description: {long_desc}
---
Body text."""

            skill_md.write_text(content, encoding="utf-8")

            passed, errors = validate_file(str(skill_md))

            assert passed is False
            error_str = "\n".join(errors)
            assert "1024" in error_str

    def test_body_too_long(self):
        """Test that body over 200 lines fails validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "recon"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"

            body_lines = ["line " + str(i) for i in range(250)]
            body_text = "\n".join(body_lines)

            content = f"""---
name: recon
description: Valid description under limit.
---
{body_text}"""

            skill_md.write_text(content, encoding="utf-8")

            passed, errors = validate_file(str(skill_md))

            assert passed is False
            error_str = "\n".join(errors)
            assert "200" in error_str

    def test_valid_skill_passes(self):
        """Test that a complete valid skill passes all checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "recon"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"

            content = """---
name: recon
description: Research and proposal gate for non-trivial coding tasks. Inspects repository state, classifies task complexity, proposes 3–7 task-specific self-rules, produces a structured report (Task / What I found / Unknowns / Anticipated failure classes / Proposed self-rules / Awaiting confirmation), then stops for user confirmation before proceeding. Designed to prevent wasted effort on misaligned plans by surfacing constraints early. Not a substitute for domain expertise—flags unknowns instead of guessing.
license: MIT
---
Recon Skill

This skill researches and proposes self-rules before any non-trivial task.

## Procedure

1. Inspect repository state
2. Classify task complexity
3. Propose 3-7 self-rules specific to THIS task
4. Produce structured report
5. Stop for user confirmation

## Self-Rule Examples

**GOOD (checkable):**
- All database migrations must be backward compatible
- Every new API endpoint must include rate-limit headers

**BAD (vague):**
- Always write good code
- Security is important

See [references/SELF_RULE_GUIDE.md](references/SELF_RULE_GUIDE.md) for details.
"""

            skill_md.write_text(content, encoding="utf-8")

            passed, errors = validate_file(str(skill_md))

            assert passed is True
            assert errors == []

    def test_unbalanced_code_fences(self):
        """Test that unbalanced code fences are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "recon"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"

            # Build content with EXACTLY ONE opening fence using bytes (no bash interference)
            # This ensures the file gets written with actual triple backticks
            backtick_bytes = b'\x60\x60\x60'  # Three 0x60 = ```
            fence_marker = backtick_bytes.decode('utf-8')

            # Create content by concatenating bytes then decoding
            raw_content = (
                b'---\n'
                b'name: recon\n'
                b'description: Valid description.\n'
                b'license: MIT\n'
                b'---\n'
            ) + fence_marker.encode('utf-8') + b'markdown fence\n\n## Some section\n'
            content = raw_content.decode('utf-8')

            skill_md.write_text(content, encoding="utf-8")

            # Debug: verify what was written
            written = skill_md.read_text(encoding="utf-8")
            lines = written.split('\n')

            # Count how many lines start with ```
            detected = []
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                if stripped.startswith(fence_marker):
                    detected.append((i+1, repr(line)))

            assert len(detected) == 1, f"Expected 1 fence at start of line, found: {detected}. Lines: {[repr(l) for l in lines[:7]]}"

            passed, errors = validate_file(str(skill_md))

            assert passed is False, f"Validation should fail but passed. Errors: {errors}"
            error_str = "\n".join(errors)
            assert "code fence" in error_str.lower(), f"'code fence' not in errors: {errors}"


class TestDefaultDirectories:
    """Tests for the default directories configuration."""

    def test_default_dirs_list_is_correct(self):
        """Test that default directories list contains exactly the 5 skill names."""
        expected = ["recon", "preflight", "hold", "scope", "budget"]
        assert DEFAULT_DIRS == expected
        assert len(DEFAULT_DIRS) == 5
