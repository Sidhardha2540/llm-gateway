"""
Per-tenant tool-call permission scoping: allow or deny tool_choice / tools in request.
"""
from typing import Any, Optional


def scope_tools_for_tenant(
    tenant_config: Optional[dict],
    tools: Optional[list[dict[str, Any]]],
    tool_choice: Optional[Any],
) -> tuple[Optional[list[dict[str, Any]]], Optional[Any]]:
    """
    If tenant has allow_tool_calls=False, strip tools and tool_choice.
    Returns (allowed_tools, allowed_tool_choice).
    """
    if tenant_config is None:
        return tools, tool_choice
    if not tenant_config.get("allow_tool_calls", True):
        return None, None
    return tools, tool_choice
