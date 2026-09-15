from __future__ import annotations


class SurfaceRenderer:
    """Optional expressive surface with no access to decision functions."""

    def render_action(self, action: str) -> str:
        if action == "rest":
            return "I am going to rest for a while."
        if action == "work":
            return "I am getting back to the task."
        if action == "idle":
            return "I am not doing anything in particular right now."
        if action == "avoid":
            return "I am keeping my distance for now."
        if action.startswith("avoid:"):
            actor = action.split(":", 1)[1]
            return f"I am keeping my distance from {actor}."
        if action.startswith("socialize:"):
            actor = action.split(":", 1)[1]
            return f"I am going to spend some time with {actor}."
        return f"I chose {action}."
