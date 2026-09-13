# me.skill - User Profile Analyzer

A comprehensive skill for analyzing and understanding user identity, behavior patterns, and preferences.

## What It Does

Synthesizes information from:
- 📝 Memory files (USER.md, MEMORY.md, daily logs)
- 🛠️ Installed skills ecosystem
- 🔧 MCP configurations
- 💬 Conversation history

To create a holistic user profile including:
- Identity & professional role
- Personality traits & communication style
- Technical skills & tool preferences
- Behavior patterns & work habits
- Learning interests & growth areas

## Trigger Phrases

- "Who am I?"
- "What do I like?"
- "What are my habits?"
- "Analyze me"
- "What's my profile?"
- "What skills should I learn?"

## Usage Examples

### Quick Profile
```
User: Who am I?
Agent: [Loads USER.md + recent skills, presents brief profile]
```

### Deep Analysis
```
User: Analyze me deeply
Agent: [Full memory scan + detailed report using template]
```

### Skill Recommendations
```
User: What should I learn next?
Agent: [Analyzes skill gaps, suggests relevant skills]
```

## Output Modes

### Brief Mode (default)
- 2-3 sentence identity summary
- Top skills & tools
- Key behavior patterns

### Detailed Mode (on request)
- Comprehensive profile (see `references/detailed-template.md`)
- Skill distribution analysis
- Growth recommendations
- Workflow insights

## Privacy & Security

✅ **Safe:**
- Analyzes patterns, not secrets
- Respects session boundaries
- Marks confidence levels

❌ **Never:**
- Exposes tokens/credentials
- Quotes private data verbatim
- Accesses MEMORY.md in group chats

## Installation

```bash
# Copy to skills directory
cp -r me ~/.openclaw/skills/
cp -r me ~/.claude/skills/
cp -r me /projects/.openclaw/skills/
```

## Development

Built with skill-creator best practices:
- Concise SKILL.md (< 500 lines)
- References split into separate files
- Helper script for skill analysis
- Template-driven detailed reports

## Files

```
me/
├── SKILL.md                           # Main skill definition
├── references/
│   ├── detailed-template.md           # Comprehensive profile template
│   └── analyze_skills.py              # Helper script for skill categorization
└── README.md                          # This file
```

## Dependencies

- Python 3.6+ (for analyze_skills.py)
- Access to memory files (workspace context)
- Read permission for skills directories

## Related Skills

- `distill-person` - Create digital humans from Git history
- `work-at-tencent` - Company system navigation

## License

Created for OpenClaw internal use.
