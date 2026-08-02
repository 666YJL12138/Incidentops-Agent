from pathlib import Path


SKILLS_DIR = Path("skills")


def load_skill(skill_name: str) -> str:
    path = SKILLS_DIR / skill_name / "SKILL.md"

    if not path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_name}")

    return path.read_text(encoding="utf-8")


def load_incident_skills() -> dict[str, str]:
    skill_names = [
        "triage-alert",
        "investigate-root-cause",
        "safe-remediation",
        "write-postmortem",
    ]

    return {
        name: load_skill(name)
        for name in skill_names
    }
