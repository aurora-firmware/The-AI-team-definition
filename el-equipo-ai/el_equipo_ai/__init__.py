"""El-equipo-AI — thin orchestration glue for Superpowers + Vibe Kanban."""

__version__ = "0.1.0"

from el_equipo_ai.main import App  # noqa: E402 — re-export for convenience

__all__ = ["App", "__version__"]
