import pytest

from apps.api import incident_store


@pytest.fixture(autouse=True)
def isolated_incident_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_incidents.db"

    monkeypatch.setattr(
        incident_store,
        "DB_PATH",
        test_db_path,
    )

    incident_store.init_db()

    yield test_db_path
