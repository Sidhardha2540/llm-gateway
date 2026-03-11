"""
System prompt isolation: ensure tenant-specific system prompt is applied and not leaked across tenants.
We prepend tenant system prompt (if any) and do not mix messages from other tenants.
"""
from typing import Any, Optional


def apply_system_prompt_isolation(
    messages: list[dict[str, Any]],
    tenant_system_prompt: Optional[str],
) -> list[dict[str, Any]]:
    """
    If tenant has a system_prompt_override, ensure it is the first system message.
    Merge with existing system content if needed; do not expose other tenants' prompts.
    """
    if not tenant_system_prompt or not tenant_system_prompt.strip():
        return messages

    out = []
    system_merged = tenant_system_prompt.strip()
    for m in messages:
        role = m.get("role", "")
        if role == "system":
            existing = (m.get("content") or "").strip()
            if existing and existing not in system_merged:
                system_merged = system_merged + "\n\n" + existing
            continue
        out.append(m)

    out.insert(0, {"role": "system", "content": system_merged})
    return out
