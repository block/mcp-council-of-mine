from src import mcp

@mcp.prompt()
def council_debate(topic: str) -> str:
    """
    Consult the Council of Mine for a debate on any topic.

    Args:
        topic: The question or topic for the council to debate
    """
    return f"""Please use the start_council_debate tool with this topic:

"{topic}"

Then call get_results() to see voting, synthesis, and the council's final decision."""


@mcp.prompt()
def ask_council(question: str) -> str:
    """
    Ask the Council of Mine for their collective wisdom on a question.

    Args:
        question: Your question for the council
    """
    return f"""The Council of Mine should debate this question:

"{question}"

Please:
1. Call start_council_debate with the question
2. Call get_results to see voting, synthesis, and the winning perspective"""


@mcp.prompt()
def council_decision(scenario: str) -> str:
    """
    Get a council decision on a scenario or dilemma.

    Args:
        scenario: The scenario requiring a decision
    """
    return f"""Present this scenario to the Council of Mine for deliberation:

"{scenario}"

Execute the debate workflow:
1. start_council_debate("{scenario}")
2. get_results()

Return the synthesis and winning opinion."""


@mcp.prompt()
def quick_poll(statement: str) -> str:
    """
    Quick council poll: get diverse perspectives on a statement.

    Args:
        statement: A statement to evaluate
    """
    return f"""Poll the Council of Mine on this statement:

"{statement}"

Run through the complete debate process and show me:
- All 9 member opinions
- Voting results
- Final synthesis"""


@mcp.prompt()
def council_wisdom() -> str:
    """
    Explore past council debates and wisdom.
    """
    return """Show me the council's past debates using list_past_debates().

If there are interesting past debates, we can view them in detail with view_debate(debate_id)."""


@mcp.prompt()
def council_help() -> str:
    """
    Learn how to use the Council of Mine server.
    """
    return """The Council of Mine has 9 members with unique personalities:

🔧 The Pragmatist - Practical, results-oriented
🌟 The Visionary - Big-picture thinker
🔗 The Systems Thinker - Sees interconnections and cascading effects
😊 The Optimist - Positive and opportunity-focused
😈 The Devil's Advocate - Challenges assumptions
🤝 The Mediator - Seeks common ground
👥 The User Advocate - Champions accessibility and usability
📜 The Traditionalist - Values proven methods
📊 The Analyst - Data-driven and logical

To start a debate:
1. start_council_debate("your topic")
2. conduct_voting()
3. get_results()

Or use prompts like:
- "council_debate" - Start a formal debate
- "ask_council" - Ask a question
- "council_decision" - Get a decision on a scenario
- "council_wisdom" - View past debates"""

