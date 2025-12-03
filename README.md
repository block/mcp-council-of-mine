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
git clone https://github.com/block/mcp-council-of-mine.git
cd mcp-council-of-mine

# Install dependencies
uv sync

# Run the server
uv run mcp_council_of_mine
```

## Adding to AI Agents

### Goose

Add to your Goose configuration (`~/.config/goose/config.yaml`):

**Option 1: Direct from GitHub**
```yaml
extensions:
  council-of-mine:
    name: CouncilOfMine
    cmd: uvx
    args:
      - --from
      - git+https://github.com/block/mcp-council-of-mine
      - mcp_council_of_mine
    enabled: true
    type: stdio
    timeout: 300
```

**Option 2: Local Installation (Use Wrapper Script)**
```yaml
extensions:
  council-of-mine:
    name: CouncilOfMine
    cmd: uvx --from /path/to/mcp-council-of-mine mcp_council_of_mine
    args: []
    enabled: true
    type: stdio
    timeout: 300
```

### Other MCP Clients

For any MCP-compatible client, it must support stdio servers *and* sampling.

## Usage

### Running the Server (Development)

You can use the MCP inspector tool to debug this server. For example, to inspect the current dev version from Github you can run the following command (requires NodeJS)

```bash
# With inspector (for debugging)
npx @modelcontextprotocol/inspector uvx --from git+https://github.com/block/mcp-council-of-mine mcp_council_of_mine
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

## Requirements

### For Direct GitHub Usage (uvx)
- UV package manager installed
- Internet connection (first run only - cached after)

## Contributing

Contributions welcome! Please ensure:
- Follows Block's code of conduct
- Tests pass
- Code is self-documenting

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
- [UV](https://docs.astral.sh/uv/) - Fast Python package manager
