from pydantic import BaseModel, Field


class IncidentState(BaseModel):
    incident_id: str
    alert: dict
    status: str = "investigating"

    skills: dict[str, str] = Field(default_factory=dict)
    timeline: list[dict] = Field(default_factory=list)
    evidence: dict = Field(default_factory=dict)
    hypotheses: list[dict] = Field(default_factory=list)
    recommended_actions: list[dict] = Field(default_factory=list)
    postmortem: dict = Field(default_factory=dict)


def add_timeline_event(state: IncidentState, step: str, message: str) -> None:
    state.timeline.append(
        {
            "step": step,
            "message": message,
        }
    )
