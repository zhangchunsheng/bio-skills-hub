#!/usr/bin/env python3
"""
Skill Categorizer

Analyzes installed skills and categorizes them by domain.
Helps understand user's technical interests and tool ecosystem.
"""

import os
import json
from pathlib import Path
from collections import defaultdict

SKILL_DIRS = [
    Path.home() / ".openclaw/skills",
    Path.home() / ".claude/skills", 
    Path.home() / ".claude-internal/skills",
    Path("/projects/.openclaw/skills"),
]

# Domain categories with keyword patterns
CATEGORIES = {
    "Development": ["code", "git", "github", "gongfeng", "claude", "codex", "programming"],
    "Enterprise": ["tapd", "wecom", "iwiki", "km", "lexiang", "eplus"],
    "Data & Analytics": ["bigdata", "datatalk", "tianqiong", "wedata", "sql", "analytics"],
    "Infrastructure": ["rainbow", "zeus", "aegis", "deploy", "monitor", "docker", "k8s"],
    "Automation": ["browser", "automation", "workflow", "script"],
    "Knowledge": ["wiki", "doc", "knowledge", "research", "paper", "arxiv"],
    "Communication": ["message", "email", "notify", "alert"],
    "Utilities": ["weather", "news", "search", "tool"],
}

def load_skill_metadata(skill_path):
    """Load SKILL.md frontmatter"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None
    
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Simple YAML parsing for name and description
                    lines = parts[1].strip().split('\n')
                    meta = {}
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            meta[key.strip()] = value.strip().strip('"')
                    return meta
    except:
        pass
    return None

def categorize_skill(skill_name, description=""):
    """Categorize skill based on name and description"""
    text = (skill_name + " " + description).lower()
    
    matched = []
    for category, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            matched.append(category)
    
    return matched if matched else ["Other"]

def analyze_skills():
    """Analyze all installed skills"""
    skills_by_category = defaultdict(list)
    all_skills = []
    
    for skill_dir in SKILL_DIRS:
        if not skill_dir.exists():
            continue
        
        for item in skill_dir.iterdir():
            if not item.is_dir():
                continue
            
            skill_name = item.name
            meta = load_skill_metadata(item)
            description = meta.get('description', '') if meta else ''
            
            skill_info = {
                'name': skill_name,
                'path': str(item),
                'description': description[:100] + '...' if len(description) > 100 else description
            }
            
            all_skills.append(skill_info)
            
            categories = categorize_skill(skill_name, description)
            for cat in categories:
                skills_by_category[cat].append(skill_info)
    
    return {
        'total': len(all_skills),
        'by_category': dict(skills_by_category),
        'all_skills': all_skills
    }

def format_output(analysis):
    """Format analysis as markdown"""
    lines = [
        f"# Skill Ecosystem Analysis",
        f"",
        f"**Total Skills**: {analysis['total']}",
        f"",
        f"## By Category",
        f""
    ]
    
    for category in sorted(analysis['by_category'].keys()):
        skills = analysis['by_category'][category]
        lines.append(f"### {category} ({len(skills)})")
        lines.append("")
        for skill in sorted(skills, key=lambda x: x['name']):
            lines.append(f"- **{skill['name']}**")
            if skill['description']:
                lines.append(f"  {skill['description']}")
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    analysis = analyze_skills()
    
    # JSON output for programmatic use
    json_output = json.dumps(analysis, indent=2, ensure_ascii=False)
    
    # Markdown output for human reading
    md_output = format_output(analysis)
    
    # Default: print markdown
    import sys
    if '--json' in sys.argv:
        print(json_output)
    else:
        print(md_output)
