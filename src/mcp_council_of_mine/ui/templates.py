import re
from mcp_ui_server import create_ui_resource
from mcp_ui_server.core import UIResource


def generate_opinions_ui(debate_id: str, prompt: str, opinions: dict) -> list[UIResource]:
    """Generate UI for displaying council member opinions"""

    opinions_html = ""
    for opinion in opinions.values():
        # Clean opinion text
        opinion_text = opinion['opinion']
        if isinstance(opinion_text, str) and opinion_text.startswith("type="):
            match = re.search(r"text=['\"](.+?)['\"]", opinion_text, re.DOTALL)
            if match:
                opinion_text = match.group(1).replace('\\n', '\n').replace("\\'", "'")

        opinions_html += f"""
        <div class="opinion-card">
            <div class="member-header">
                <span class="icon">{get_member_icon(opinion['member_id'])}</span>
                <h3>{opinion['member_name']}</h3>
            </div>
            <p class="opinion-text">{opinion_text}</p>
        </div>
        """

    html = f"""
    <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            html, body {{
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }}
            .container {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-size: 14px;
                width: 100%;
                margin: 0;
                overflow-x: hidden;
            }}
            .header {{
                text-align: center;
                color: white;
                margin-bottom: 16px;
            }}
            .header h1 {{
                font-size: 24px;
                margin-bottom: 8px;
            }}
            .prompt-box {{
                background: rgba(255, 255, 255, 0.95);
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .prompt-box h2 {{
                font-size: 14px;
                color: #667eea;
                margin-bottom: 6px;
            }}
            .prompt-text {{
                font-size: 15px;
                color: #333;
                font-weight: 500;
            }}
            .opinions-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
                gap: 12px;
                margin-bottom: 16px;
            }}
            .opinion-card {{
                background: white;
                border-radius: 8px;
                padding: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
                min-width: 0;
                overflow-wrap: break-word;
            }}
            .opinion-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
            .member-header {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
                padding-bottom: 8px;
                border-bottom: 2px solid #f0f0f0;
            }}
            .icon {{
                font-size: 24px;
                margin-right: 8px;
            }}
            .member-header h3 {{
                font-size: 15px;
                color: #333;
            }}
            .opinion-text {{
                color: #555;
                line-height: 1.5;
                font-size: 13px;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            .status-box {{
                background: rgba(255, 255, 255, 0.95);
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                color: #667eea;
                font-weight: 500;
                font-size: 13px;
            }}
        </style>
        <div class="container">
            <div class="header">
                <h1>🏛️ Council of Mine Debate</h1>
                <p>Debate ID: {debate_id}</p>
            </div>

            <div class="prompt-box">
                <h2>Debate Topic:</h2>
                <p class="prompt-text">{prompt}</p>
            </div>

            <div class="opinions-grid">
                {opinions_html}
            </div>

            <div class="status-box">
                ✅ All 9 council members have shared their opinions
            </div>
        </div>

        <script>
            // Auto-resize iframe to fit content
            function notifyResize() {{
                const container = document.querySelector('.container');
                if (container && window.parent) {{
                    const height = container.scrollHeight;
                    const width = container.scrollWidth;
                    window.parent.postMessage({{
                        type: 'ui-size-change',
                        payload: {{
                            height: height,
                            width: width
                        }}
                    }}, '*');
                }}
            }}

            // Watch for size changes
            const observer = new ResizeObserver(() => {{
                notifyResize();
            }});

            const container = document.querySelector('.container');
            if (container) {{
                observer.observe(container);
            }}

            // Initial resize notification
            setTimeout(notifyResize, 100);
        </script>
    """

    ui_resource = create_ui_resource({
        "uri": f"ui://council/debate/{debate_id}/opinions",
        "content": {
            "type": "rawHtml",
            "htmlString": html
        },
        "encoding": "text",
        "uiMetadata": {
        }
    })

    return [ui_resource]


def generate_results_ui(results: dict) -> list[UIResource]:
    """Generate UI for displaying debate results with synthesis"""

    # Clean up synthesis text if it has object representation
    synthesis = results['synthesis']
    if isinstance(synthesis, str) and synthesis.startswith("type="):
        # Extract text from object representation with greedy regex
        match = re.search(r"text=['\"](.+)['\"](?:\s+(?:annotations|meta)=|$)", synthesis, re.DOTALL)
        if match:
            synthesis = match.group(1).replace('\\n', '\n').replace("\\'", "'")

    # If empty or still broken, show error
    if not synthesis or synthesis.startswith("type="):
        synthesis = "Error: Unable to extract synthesis text"

    winners_html = ""
    for winner in results["winners"]:
        # Clean winner opinion text
        winner_opinion = winner['opinion']
        if isinstance(winner_opinion, str) and winner_opinion.startswith("type="):
            match = re.search(r"text=['\"](.+?)['\"]", winner_opinion, re.DOTALL)
            if match:
                winner_opinion = match.group(1).replace('\\n', '\n').replace("\\'", "'")

        winners_html += f"""
        <div class="winner-card">
            <div class="winner-badge">🏆 WINNER</div>
            <div class="member-header">
                <span class="icon">{get_member_icon(winner['member_id'])}</span>
                <h3>{winner['member_name']}</h3>
            </div>
            <p class="winner-opinion">{winner_opinion}</p>
            <div class="vote-count">{winner['votes_received']} vote(s)</div>
        </div>
        """

    votes_html = ""
    for vote in results["all_votes"]:
        # Clean up reasoning text - remove object repr if present
        reasoning = vote['reasoning']
        if reasoning.startswith("type="):
            # Extract text from object representation
            match = re.search(r"text=['\"](.+?)['\"]", reasoning)
            if match:
                reasoning = match.group(1).replace('\\n', ' ').replace("\\'", "'")
            else:
                reasoning = ""

        # Remove VOTE: and REASONING: prefixes if present
        reasoning = re.sub(r'^VOTE:\s*\d+\s*\n*', '', reasoning)
        reasoning = re.sub(r'REASONING:\s*', '', reasoning, flags=re.IGNORECASE)
        reasoning = reasoning.strip()

        votes_html += f"""
        <div class="vote-item">
            <div class="vote-header">
                <strong>{vote['voter_name']}</strong> voted for <strong>{vote['voted_for']}</strong>
            </div>
            <div class="vote-reasoning"><b>Reasoning:</b> {reasoning}</div>
        </div>
        """

    html = f"""
    <style>
             * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            html, body {{
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }}
            .container {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-size: 14px;
                width: 100%;
                margin: 0;
                overflow-x: hidden;
            }}
            .header {{
                text-align: center;
                color: white;
                margin-bottom: 16px;
            }}
            .header h1 {{
                font-size: 24px;
                margin-bottom: 8px;
            }}
            .prompt-box {{
                background: rgba(255, 255, 255, 0.95);
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section {{
                background: rgba(255, 255, 255, 0.95);
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                min-width: 0;
                overflow-wrap: break-word;
            }}
            .section h2 {{
                font-size: 18px;
                color: #667eea;
                margin-bottom: 12px;
            }}
            .winner-card {{
                background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 12px;
                position: relative;
                min-width: 0;
                overflow-wrap: break-word;
            }}
            .winner-badge {{
                position: absolute;
                top: -8px;
                right: 12px;
                background: #ff6b6b;
                color: white;
                padding: 6px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            .member-header {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }}
            .icon {{
                font-size: 24px;
                margin-right: 8px;
            }}
            .member-header h3 {{
                font-size: 16px;
                color: #333;
            }}
            .winner-opinion {{
                color: #333;
                line-height: 1.5;
                font-size: 13px;
                margin-bottom: 8px;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            .vote-count {{
                font-weight: bold;
                color: #667eea;
                font-size: 14px;
            }}
            .synthesis-box {{
                background: #f8f9fa;
                border-left: 3px solid #667eea;
                padding: 12px;
                border-radius: 6px;
                line-height: 1.6;
                font-size: 13px;
                color: #333;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            .vote-item {{
                background: #f8f9fa;
                padding: 10px;
                border-radius: 6px;
                margin-bottom: 8px;
                min-width: 0;
                overflow-wrap: break-word;
            }}
            .vote-header {{
                margin-bottom: 6px;
                color: #333;
                font-size: 13px;
            }}
            .vote-reasoning {{
                color: #555;
                font-size: 13px;
                line-height: 1.5;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            .vote-reasoning b {{
                color: #667eea;
                font-weight: 600;
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                margin-top: 12px;
            }}
            .stat {{
                text-align: center;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
            }}
            .stat-label {{
                font-size: 12px;
                color: #666;
                margin-top: 4px;
            }}
        </style>
        <div class="container">
            <div class="header">
                <h1>🏛️ Council Decision Results</h1>
                <p>Debate ID: {results['debate_id']}</p>
            </div>

            <div class="prompt-box">
                <h2>Debate Topic:</h2>
                <p class="prompt-text">{results['prompt']}</p>
            </div>

            <div class="section">
                <h2>🏆 Winning Opinion</h2>
                {winners_html}
            </div>

            <div class="section">
                <h2>🎯 Council Synthesis</h2>
                <div class="synthesis-box">
                    {synthesis}
                </div>
            </div>

            <div class="section">
                <h2>🗳️ All Votes & Reasoning</h2>
                {votes_html}
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{results['total_votes_cast']}</div>
                        <div class="stat-label">Total Votes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{len(results['winners'])}</div>
                        <div class="stat-label">Winner(s)</div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Auto-resize iframe to fit content
            function notifyResize() {{
                const container = document.querySelector('.container');
                if (container && window.parent) {{
                    const height = container.scrollHeight;
                    const width = container.scrollWidth;
                    window.parent.postMessage({{
                        type: 'ui-size-change',
                        payload: {{
                            height: height,
                            width: width
                        }}
                    }}, '*');
                }}
            }}

            // Watch for size changes
            const observer = new ResizeObserver(() => {{
                notifyResize();
            }});

            const container = document.querySelector('.container');
            if (container) {{
                observer.observe(container);
            }}

            // Initial resize notification
            setTimeout(notifyResize, 100);
        </script>
    """

    ui_resource = create_ui_resource({
        "uri": f"ui://council/results/{results['debate_id']}",
        "content": {
            "type": "rawHtml",
            "htmlString": html
        },
        "encoding": "text",
        "uiMetadata": {
        }
    })

    return [ui_resource]


def get_member_icon(member_id: int) -> str:
    """Get emoji icon for member by ID"""
    icons = {
        1: "🔧",  # Pragmatist
        2: "🌟",  # Visionary
        3: "🤔",  # Skeptic
        4: "😊",  # Optimist
        5: "😈",  # Devil's Advocate
        6: "🤝",  # Mediator
        7: "💡",  # Innovator
        8: "📜",  # Traditionalist
        9: "📊"   # Analyst
    }
    return icons.get(member_id, "👤")
