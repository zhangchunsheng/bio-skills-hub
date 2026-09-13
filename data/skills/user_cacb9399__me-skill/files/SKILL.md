---
name: me
description: "Analyze and understand the user's identity, role, personality, behavior patterns, and preferences based on conversation history, memory files (MEMORY.md, USER.md, daily notes), installed skills, and MCP configurations. Use when the user asks questions about themselves like 'who am I?', 'what do I like?', 'what are my habits?', 'analyze me', 'what's my profile?', or when needing to understand user context for personalized recommendations."
---

# Me - User Profile Analyzer

This skill analyzes the user's digital footprint to understand their identity, role, personality, and preferences.

## What This Skill Does

Synthesizes information from multiple sources to create a comprehensive user profile:

1. **Identity & Role**: Who the user is professionally and personally
2. **Personality Traits**: Communication style, decision-making patterns, values
3. **Technical Profile**: Skills, tools, frameworks, languages they use
4. **Behavior Patterns**: Work habits, time management, problem-solving approaches
5. **Preferences**: Favorite tools, workflows, communication channels
6. **Growth Areas**: Learning interests, challenges, goals

## Data Sources Priority

Analyze in this order:

1. **Memory Files** (highest authority)
   - `USER.md` - Explicit user profile
   - `MEMORY.md` - Long-term curated memories
   - `memory/YYYY-MM-DD.md` - Recent daily logs (last 7-14 days)

2. **Workspace Context**
   - `SOUL.md` - Persona preferences
   - `IDENTITY.md` - Self-identified traits
   - `TOOLS.md` - Tool preferences

3. **Installed Skills**
   - Skill names and categories reveal interests
   - Technical domains (e.g., `gongfeng`, `tapd`, `datatalk-card-query`)
   - Business domains (e.g., `km`, `iwiki`, `lexiang-knowledge-base`)
   - Personal interests (e.g., `weather`, `hackernews`, `arxiv-watcher`)

4. **MCP Configurations**
   - Configured services reveal workflow integrations
   - API connections show tool ecosystem

5. **Session History** (when available)
   - Recent conversation topics
   - Question patterns
   - Task types
   - Communication style

## Analysis Workflow

### Step 1: Load Memory Files

Read in order (stop if file doesn't exist):

```bash
# Core identity
read USER.md
read IDENTITY.md

# Long-term memory (main session only)
read MEMORY.md

# Recent context (last 14 days)
ls memory/ | grep -E "202[0-9]-[0-9]{2}-[0-9]{2}\.md" | sort -r | head -14
```

### Step 2: Analyze Installed Skills

```bash
# List all skills
ls ~/.openclaw/skills/
ls /projects/.openclaw/skills/
ls ~/.claude/skills/
```

Categorize by domain:
- **Development**: `gongfeng`, `claude-internal`, `distill-person`
- **Enterprise Tools**: `tapd`, `iwiki`, `km`, `lexiang-knowledge-base`, `wecom-*`
- **Data & Analytics**: `datatalk-card-query`, `eplus`, `tencent-bigdata`
- **Automation**: `rainbow-config`, `browser-operation`
- **Knowledge**: `research-paper-writer`, `arxiv-watcher`, `hackernews`
- **Utilities**: `weather`, `news-summary`

### Step 3: Check MCP Integrations

```bash
# Gateway config
openclaw config | grep -A 20 "mcpConfig"
```

Extract:
- Configured MCP servers
- Authentication tokens (presence, not values)
- Service endpoints

### Step 4: Analyze Session Context

If session history available:
- Recent topics (last 50 messages)
- Command patterns
- Tool usage frequency
- Time-of-day patterns

### Step 5: Synthesize Profile

Create structured profile:

#### 🧑 Identity
- Name / Handle
- Role / Title
- Team / Organization
- Contact preferences

#### 🎭 Personality
- Communication style (formal/casual, concise/detailed)
- Decision-making (analytical/intuitive, fast/deliberate)
- Values (efficiency, quality, innovation, collaboration)

#### 💻 Technical Profile
- Primary languages (from repos/skills)
- Framework preferences
- Tool ecosystem
- Skill level indicators

#### ⏰ Behavior Patterns
- Work hours (from timestamp analysis)
- Task types (development, research, coordination)
- Problem-solving style
- Collaboration patterns

#### ❤️ Preferences
- Favorite tools
- Preferred workflows
- Communication channels
- Information sources

#### 🌱 Growth Indicators
- Learning interests (new skills installed)
- Challenges (repeated error patterns)
- Goals (from memory notes)

## Output Format

### Brief Mode (default)

```markdown
## 🧑 Who You Are

[2-3 sentence summary]

## 💼 Professional Profile

**Role**: [inferred role]
**Domain**: [primary domain]
**Tools**: [top 5 tools]

## 🎯 Key Patterns

- **Work Style**: [pattern 1]
- **Interests**: [pattern 2]
- **Preferences**: [pattern 3]

## 📊 Skill Distribution

[Simple categorized list of installed skills]
```

### Detailed Mode (when requested)

Use `references/detailed-template.md` for comprehensive analysis.

## Privacy & Security

**Always respect privacy:**

- Never expose secrets, tokens, or credentials
- Summarize patterns, don't quote verbatim private content
- Distinguish between facts (from files) and inferences
- Mark confidence levels: "确定" / "推测" / "可能"

**Data boundaries:**

- Main session: full memory access
- Group chats: only shared context (no MEMORY.md)
- Public contexts: only public profile data

## Handling Common Questions

### "Who am I?"

Load USER.md + IDENTITY.md, present brief profile.

### "What do I like?"

Analyze preferences from:
- Favorite tools (TOOLS.md)
- Installed skills (interest domains)
- Repeated topics (memory files)

### "What are my habits?"

Analyze patterns from:
- Daily logs (memory/YYYY-MM-DD.md)
- Timestamp distributions
- Task types frequency

### "Analyze me deeply"

Run full analysis, use detailed template.

### "What skills should I learn?"

Compare:
- Current skill set (installed skills)
- Recent challenges (error patterns in logs)
- Growth areas (mentioned goals in MEMORY.md)

Suggest skills from knowledge gaps.

## Quality Checks

Before presenting profile:

- [ ] All data sources checked (memory files, skills, MCPs)
- [ ] Inferences clearly marked vs. facts
- [ ] No private data exposed
- [ ] Confidence levels indicated
- [ ] Profile is coherent and actionable

## Example Usage

**User:** "Who am I?"

**Agent:**
1. Read USER.md, IDENTITY.md
2. Scan installed skills
3. Check recent memory logs
4. Present brief profile

**User:** "Analyze my interests deeply"

**Agent:**
1. Full memory scan (14 days)
2. Skill categorization
3. Topic frequency analysis
4. Load detailed template
5. Present comprehensive report
