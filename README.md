# Council of Mine MCP Server

An innovative MCP server featuring 9 council members with distinct personalities who debate topics, vote on each other's opinions, and generate synthesized conclusions through AI-powered deliberation.

## Features

- **9 Unique Council Members**: Each with distinct archetypes and personalities
  - 🔧 The Pragmatist - Practical, results-oriented
  - 🌟 The Visionary - Big-picture thinker
  - 🔗 The Systems Thinker - Sees interconnections and cascading effects
  - 😊 The Optimist - Positive and opportunity-focused
  - 😈 The Devil's Advocate - Challenges all assumptions
  - 🤝 The Mediator - Seeks common ground
  - 👥 The User Advocate - Champions accessibility and usability
  - 📜 The Traditionalist - Values proven methods
  - 📊 The Analyst - Data-driven and logical

- **Individual Perspectives + Synthesis**: See ALL 9 unique opinions alongside the synthesized conclusion - never just a summary
- **Automatic Debate System**: Members form opinions using LLM sampling
- **Democratic Voting**: Each member votes for the opinion that best aligns with their values
- **Full Voting Transparency**: See every individual vote and the reasoning behind each decision
- **AI-Powered Synthesis**: Generates unified conclusions from diverse perspectives
- **Text-Based Output**: Clean, formatted text responses for all AI agents
- **Persistent History**: File-based storage of all debates

## Quick Start

### Option 1: Run Directly from GitHub (Recommended)

No installation required! Use `uvx` to run directly from the GitHub repository:

```bash
uvx --from git+https://github.com/block/mcp-council-of-mine mcp_council_of_mine
```

### Option 2: Clone and Run Locally

```bash
# Clone the repository
git clone https://github.com/block/council-of-mine.git
cd council-of-mine

# Install dependencies
uv sync

# Run the server
PYTHONPATH=. uv run fastmcp dev src/main.py
```

## Adding to AI Agents

### Goose

Add to your Goose configuration (`~/.config/goose/config.yaml`):

**Option 1: Direct from GitHub**
```yaml
extensions:
  council-of-mine:
    name: Council of Mine
    cmd: uvx
    args:
      - --from
      - git+https://github.com/YOUR_USERNAME/council-of-mine
      - fastmcp
      - run
      - src/main.py
    enabled: true
    type: stdio
    timeout: 300
```

**Option 2: Local Installation (Use Wrapper Script)**
```yaml
extensions:
  council-of-mine:
    name: Council of Mine
    cmd: uvx --from /path/to/mcp-council-of-mine mcp_council_of_mine
    args: []
    enabled: true
    type: stdio
    timeout: 300
```

**Note:** Goose intercepts Python/uvx commands and can break the working directory. The wrapper script in `scripts/council-mcp` handles this, or use the direct GitHub method.

### Other MCP Clients

For any MCP-compatible client, it must support stdio servers *and* sampling.

## Usage

### Running the Server (Development)

```bash
# With inspector (for debugging)
PYTHONPATH=. uv run fastmcp dev src/main.py

# Or directly from GitHub
uvx --from git+https://github.com/YOUR_USERNAME/council-of-mine fastmcp dev src/main.py
```

## Available Tools

### 1. `start_council_debate(prompt)`

Initiate a new council debate where all 9 members generate opinions on your prompt.

**Args:**
- `prompt` (str): The topic or question to debate

**Returns:**
- Formatted text displaying ALL 9 individual council member opinions
- Each member's unique perspective shown separately with their name and icon
- Preserves the full diversity of viewpoints

**Example:**
```
Use the start_council_debate tool with:
prompt: "Should we prioritize speed or quality in software development?"

Response will show all 9 members' opinions, like:
🔧 THE PRAGMATIST
[Their opinion...]

🌟 THE VISIONARY
[Their opinion...]
... (all 9 members)
```

### 2. `conduct_voting()`

Automatically conduct voting where each member evaluates all opinions (except their own) and votes for the one that best aligns with their perspective.

**Returns:**
- Dictionary with complete voting transparency:
  - `status`: voting completion status
  - `total_votes`: number of votes cast
  - `individual_votes`: detailed list showing who voted for whom and why
  - Each vote includes voter name, their choice, and reasoning

**Example:**
```
After starting a debate, call conduct_voting to have members vote.
The response will show all individual voting decisions with reasoning.
```

### 3. `get_results()`

Generate comprehensive results including all opinions, winner(s), vote reasoning, and AI-generated synthesis.

**Returns:**
- Formatted text with complete debate results:
  - **ALL 9 individual opinions** from each council member with their vote counts
  - Winning opinion(s) highlighted
  - **ALL individual votes**: see exactly who voted for whom
  - Detailed reasoning from each member explaining their vote
  - AI-synthesized summary of the debate
  - Debate is automatically saved to history

**Example:**
```
After voting completes, call get_results to see all opinions,
winning opinion, all individual votes with reasoning, and synthesis
```

### 4. `list_past_debates()`

List all previously saved debates.

**Returns:**
- Dictionary with list of debates (ID, prompt, timestamp)

### 5. `view_debate(debate_id)`

View complete details of a past debate.

**Args:**
- `debate_id` (str): Debate ID in format YYYYMMDD_HHMMSS

**Returns:**
- Complete debate data including:
  - All member opinions
  - Full vote breakdown (who voted for whom)
  - Vote reasoning from each member
  - Results and synthesis

### 6. `get_current_debate_status()`

Check the status of any currently active debate.

**Returns:**
- Current debate information or "no active debate" message

## Typical Workflow

1. **Start Debate**: Call `start_council_debate` with your topic
   - 9 members generate opinions via LLM sampling
   - Interactive UI displays all opinions

2. **Conduct Voting**: Call `conduct_voting`
   - Each member votes for the opinion that resonates with them
   - Members provide reasoning for their votes
   - Returns detailed breakdown of all individual votes

3. **View Results**: Call `get_results`
   - **See ALL 9 individual opinions** with vote counts for each
   - Winning opinion(s) highlighted
   - **View ALL individual votes**: exactly who voted for whom
   - Read detailed vote reasoning from each member
   - Get AI-generated synthesis of all perspectives
   - Debate is saved to file

4. **Review History**: Use `list_past_debates` and `view_debate` to revisit past discussions

## Example Session

```
1. start_council_debate("Should we use TypeScript or JavaScript for our new project?")
   → 9 members share their opinions
   → Interactive UI shows all perspectives

2. conduct_voting()
   → Members vote on opinions
   → Reasoning collected for each vote
   → Individual votes displayed (who voted for whom)

3. get_results()
   → ALL 9 individual opinions displayed with vote counts
   → Winner announced
   → ALL individual votes shown with reasoning
   → Vote distribution displayed
   → Synthesis generated
   → Debate saved as debates/20250105_143022.json

4. list_past_debates()
   → View all historical debates

5. view_debate("20250105_143022")
   → Revisit the full debate
```

## Architecture

### LLM Sampling

The server uses MCP sampling (`ctx.sample()`) to make approximately 28 LLM calls per complete debate:
- 9 calls for opinion generation
- 9 calls for voting
- 9 calls for vote reasoning
- 1 call for final synthesis

This distributed approach allows clients to control model selection and costs.

### Individual Perspectives + Synthesis

A key differentiator: you get BOTH individual perspectives AND synthesized conclusions:
- **All individual opinions preserved**: Every council member's unique perspective is shown, not just the winner
- **Vote counts displayed**: See how many votes each opinion received
- **Synthesis provided**: AI-generated summary that incorporates all viewpoints
- **Never just a summary**: Unlike other tools that only show aggregated results, you see the full diversity of thought

### Full Voting Transparency

Every vote is tracked and displayed with complete transparency:
- Individual votes: see exactly which member voted for which opinion
- Vote reasoning: each member explains why they voted as they did
- Available in `conduct_voting()` response, `get_results()` output, and `view_debate()` data
- No hidden voting - all decisions are visible to agents and users

### File-Based Persistence

Debates are saved as JSON files in the `debates/` directory:
- Timestamped filenames (YYYYMMDD_HHMMSS.json)
- Complete debate history including all opinions, votes, and results
- Individual votes and reasoning preserved in saved files
- Easy to backup, share, or analyze

### Security Features

The server includes robust security protections:
- **Path traversal prevention**: Validates all file access
- **Prompt injection detection**: Identifies and blocks malicious prompts
- **Input sanitization**: Removes control characters and limits length
- **Length limits**: Prompts (2000 chars), opinions (2000 chars), reasoning (1000 chars)
- **Safe exception handling**: No internal details leaked in errors

See `docs/SECURITY_REVIEW.md` and `docs/SECURITY_FIXES.md` for details.

## Development

### Project Structure

```
council-of-mine/
├── docs/                 # Documentation
│   ├── CLAUDE.md
│   ├── COUNCIL_MEMBERS.md
│   ├── SECURITY_REVIEW.md
│   └── SECURITY_FIXES.md
├── tests/                # Test suite
│   ├── unit/
│   │   └── test_security.py
│   └── integration/
├── scripts/              # Utility scripts
│   ├── council-mcp       # Goose-compatible launcher
│   └── run-server.sh
├── debates/              # Saved debate JSON files
├── src/                  # Source code
│   ├── server.py         # FastMCP instance
│   ├── main.py           # Entry point
│   ├── security.py       # Security validation
│   ├── prompts.py        # Trigger prompts
│   ├── council/
│   │   ├── members.py    # 9 member definitions
│   │   └── state.py      # State management
│   └── tools/
│       ├── debate.py     # Debate initiation
│       ├── voting.py     # Voting system
│       ├── results.py    # Results generation
│       └── history.py    # History tools
├── pyproject.toml        # Project config
└── uv.lock               # Lockfile
```

### Running Tests

```bash
# Run all tests
PYTHONPATH=. pytest tests/

# Run unit tests only
PYTHONPATH=. pytest tests/unit/

# Run specific test file
PYTHONPATH=. python tests/unit/test_security.py

# Run with coverage
PYTHONPATH=. pytest tests/ --cov=src
```

### Code Style

This project follows the user's coding preferences:
- English only for all code, comments, and docs
- Self-documenting code over comments
- Using `rg` over `grep`, `fd` over `find`

## Requirements

### For Direct GitHub Usage (uvx)
- UV package manager installed
- Internet connection (first run only - cached after)

### For Local Development
- Python >=3.10
- UV package manager
- Dependencies: `fastmcp>=2.13.0.2`

## Contributing

Contributions welcome! Please ensure:
- All code is in English
- Tests pass
- Code is self-documenting
- UI gracefully degrades for non-UI clients

## Troubleshooting

### Sampling Not Working

Ensure your MCP client supports sampling. Some clients may not have full sampling support yet. The server will report errors if sampling fails.

### Updates Not Reflecting

`uvx` caches the package. To force a fresh install:

```bash
# Clear uvx cache
uvx --force --from git+https://github.com/block/mcp-council-of-mine mcp_council_of_mine
```

## Credits

Built with:
- [FastMCP](https://gofastmcp.com) - Python MCP server framework
- [MCP-UI](https://mcpui.dev) - Interactive UI for MCP
- [UV](https://docs.astral.sh/uv/) - Fast Python package manager
