import logging
from src import mcp
from src.council.state import get_state_manager
from fastmcp import Context


@mcp.tool()
def list_past_debates() -> dict:
    """
    List all past debates stored in the debates directory.
    Shows debate ID, prompt, timestamp, and whether results are available.

    Returns:
        Dictionary with list of past debates
    """
    state = get_state_manager()
    debates = state.list_debates()

    return {
        "total_debates": len(debates),
        "debates": debates
    }


@mcp.tool()
def view_debate(debate_id: str, ctx: Context = None) -> dict:
    """
    View a complete past debate by its ID.
    Returns all opinions, votes, and results for the specified debate.

    Args:
        debate_id: The unique ID of the debate to view (format: YYYYMMDD_HHMMSS)

    Returns:
        Complete debate data including all opinions, votes, and results
    """
    state = get_state_manager()

    try:
        debate = state.load_debate(debate_id)
        if ctx:
            ctx.info(f"Successfully loaded debate: {debate_id}")
        return debate
    except ValueError as e:
        if ctx:
            ctx.warning(f"Invalid debate_id: {debate_id}")
        logging.warning(f"Invalid debate_id attempted: {debate_id}")
        return {"error": str(e)}
    except FileNotFoundError:
        if ctx:
            ctx.warning(f"Debate not found: {debate_id}")
        return {"error": f"Debate {debate_id} not found"}
    except Exception as e:
        if ctx:
            ctx.warning("Error loading debate")
        logging.error(f"Unexpected error loading debate {debate_id}: {e}")
        return {"error": "An error occurred loading the debate"}


@mcp.tool()
def get_current_debate_status() -> dict:
    """
    Get the status of the current active debate (if any).

    Returns:
        Current debate information or message if no active debate
    """
    state = get_state_manager()
    current = state.get_current_debate()

    if not current:
        return {"status": "no_active_debate", "message": "No debate currently in progress"}

    return {
        "status": "active",
        "debate_id": current["debate_id"],
        "prompt": current["prompt"],
        "opinions_count": len(current["opinions"]),
        "votes_count": len(current["votes"]),
        "has_results": current["results"] is not None
    }
