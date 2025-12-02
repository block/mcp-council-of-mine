from fastmcp import FastMCP

INSTRUCTIONS = """
Council of Mine is an MCP server that simulates a democratic council of 9 AI-powered members with distinct personalities who debate topics and vote on the best perspectives.

## What it does
The council engages in a structured debate process:
1. Each of the 9 members generates an opinion on your topic from their unique perspective
2. Members vote for the opinions they find most aligned with their values (excluding their own)
3. Results show ALL individual opinions with vote counts, winners, individual vote reasoning, and an AI-generated synthesis

**Key Feature**: You see BOTH the individual perspectives AND the synthesized conclusion - never just a summary.

## When to use this server
Use Council of Mine when you need:
- Diverse perspectives on complex topics or decisions
- Democratic evaluation of ideas through voting
- Balanced consideration of practical, visionary, and analytical viewpoints
- Historical reference to past debates and decisions

## The 9 Council Members
🔧 The Pragmatist - Practical, results-oriented thinking focused on feasibility
🌟 The Visionary - Big-picture, transformative potential
🔗 The Systems Thinker - Interconnections and cascading effects
😊 The Optimist - Positive opportunities and potential
😈 The Devil's Advocate - Challenges assumptions and explores alternatives
🤝 The Mediator - Common ground and consensus building
👥 The User Advocate - Accessibility, usability, and inclusion
📜 The Traditionalist - Time-tested approaches and proven methods
📊 The Analyst - Data-driven, logical, measurement-focused

## Available Tools

### Core Debate Workflow (use in sequence)
1. **start_council_debate(prompt)** - Initiates a new debate on your topic
   - All 9 members each generate an opinion via LLM sampling
   - Returns formatted text showing ALL individual opinions with member names and perspectives
   - Each member's unique viewpoint is preserved and displayed separately

2. **conduct_voting()** - Members vote on opinions (must run after start_council_debate)
   - Each member votes for opinions aligning with their values
   - Members cannot vote for their own opinion
   - Returns detailed vote information including who voted for whom with reasoning
   - Agents can see individual voting decisions and rationale

3. **get_results()** - Generates final results (must run after conduct_voting)
   - **Shows ALL 9 individual opinions** from each council member with vote counts
   - Highlights winning opinion(s)
   - **Displays ALL individual votes**: see exactly who voted for whom
   - Includes detailed reasoning from each member explaining their vote
   - AI-synthesized summary incorporating all perspectives
   - Saves debate to history

### History & Status Tools
- **list_past_debates()** - View all historical debates with metadata
- **view_debate(debate_id)** - Retrieve complete data for a specific past debate
  - Includes all opinions, individual votes, and results
  - Full vote breakdown showing each member's vote and reasoning
- **get_current_debate_status()** - Check the status of the current active debate

## Typical Usage Pattern

For a new debate:
1. Call start_council_debate("Should we implement feature X?")
2. Call conduct_voting()
3. Call get_results()

To reference past debates:
1. Call list_past_debates() to see available debates
2. Call view_debate(debate_id) to see specific debate details

## Important Notes
- Only one debate can be active at a time
- Must complete the full workflow (start → vote → results) before starting a new debate
- Each complete debate makes ~28 LLM calls (9 opinions + 9 votes + 9 reasoning + 1 synthesis)
- All debates are automatically saved to history when get_results() is called
- **Full voting transparency**: All individual votes and reasoning are visible to agents
  - See exactly which members voted for which opinions
  - Access each member's reasoning for their vote choice
- The council provides balanced perspectives, not definitive answers
- Results include both democratic voting outcomes and AI synthesis for comprehensive insight
"""

mcp = FastMCP(name="council-of-mine", instructions=INSTRUCTIONS)

from mcp_council_of_mine import tools  # noqa: F401, E402
from mcp_council_of_mine import prompts  # noqa: F401, E402


def main():
    mcp.run()

if __name__ == "__main__":
    main()
