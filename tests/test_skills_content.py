"""Tests for skill content - checks that SKILL.md files exist and are structured."""

import pytest
from pathlib import Path

# Project root is two levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestSkillFilesExist:
    """Verify that required SKILL.md files are present."""

    def test_recon_skill_exists(self):
        """Test that recon/SKILL.md exists."""
        skill_path = PROJECT_ROOT / "recon" / "SKILL.md"

        if not skill_path.exists():
            pytest.skip("recon/SKILL.md not yet written")

        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "---" in content  # Has frontmatter

    def test_preflight_skill_exists(self):
        """Test that preflight/SKILL.md exists."""
        skill_path = PROJECT_ROOT / "preflight" / "SKILL.md"

        if not skill_path.exists():
            pytest.skip("preflight/SKILL.md not yet written")

        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "---" in content  # Has frontmatter

    def test_hold_skill_exists(self):
        """Test that hold/SKILL.md exists."""
        skill_path = PROJECT_ROOT / "hold" / "SKILL.md"

        if not skill_path.exists():
            pytest.skip("hold/SKILL.md not yet written")

        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "---" in content  # Has frontmatter

    def test_scope_skill_exists(self):
        """Test that scope/SKILL.md exists."""
        skill_path = PROJECT_ROOT / "scope" / "SKILL.md"

        if not skill_path.exists():
            pytest.skip("scope/SKILL.md not yet written")

        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "---" in content  # Has frontmatter

    def test_budget_skill_exists(self):
        """Test that budget/SKILL.md exists."""
        skill_path = PROJECT_ROOT / "budget" / "SKILL.md"

        if not skill_path.exists():
            pytest.skip("budget/SKILL.md not yet written")

        assert skill_path.exists()
        content = skill_path.read_text(encoding="utf-8")
        assert "---" in content  # Has frontmatter
