#!/usr/bin/env python3
"""Quick validation for health-question-generator skill."""

import sys
import yaml
from pathlib import Path

def validate_skill():
    """Validate SKILL.md frontmatter and directory structure."""

    skill_path = Path(__file__).parent.parent
    skill_md = skill_path / "SKILL.md"

    # Check SKILL.md exists
    if not skill_md.exists():
        print("❌ SKILL.md not found")
        return False

    # Read and validate frontmatter
    content = skill_md.read_text()

    if not content.startswith("---\n"):
        print("❌ SKILL.md missing frontmatter delimiter")
        return False

    try:
        frontmatter = content.split("---", 2)[1]
        fm_data = yaml.safe_load(frontmatter)
    except Exception as e:
        print(f"❌ Invalid YAML in frontmatter: {e}")
        return False

    # Check required fields
    if "name" not in fm_data:
        print("❌ Missing 'name' in frontmatter")
        return False
    if "description" not in fm_data:
        print("❌ Missing 'description' in frontmatter")
        return False

    # Validate directory structure
    expected_dirs = ["references", "assets", "scripts"]
    for dir_name in expected_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            print(f"❌ Expected directory '{dir_name}' not found")
            return False

    # Check for at least 3 reference files
    ref_files = list((skill_path / "references").glob("*.md"))
    if len(ref_files) < 3:
        print(f"❌ Expected at least 3 reference files, found {len(ref_files)}")
        return False

    # All checks passed
    print("✅ Skill validation passed!")
    print(f"   - Name: {fm_data['name']}")
    print(f"   - Description: {fm_data['description']}")
    print(f"   - Reference files: {len(ref_files)}")
    print(f"   - Directory structure: OK")

    return True

if __name__ == "__main__":
    success = validate_skill()
    sys.exit(0 if success else 1)