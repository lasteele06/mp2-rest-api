import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from main import app
from src import DatasetStorage


@pytest.fixture
def client(monkeypatch):
    test_storage = DatasetStorage()
    monkeypatch.setattr("main.storage", test_storage)

    with TestClient(app) as test_client:
        yield test_client



@pytest.fixture
def sample_csv_bytes():
    filepath = Path(__file__).parent.parent / "fixtures" / "sample_data.csv"
    return filepath.read_bytes()


@pytest.fixture
def uploaded_dataset_id(client, sample_csv_bytes):
    response = client.post(
        "/upload",
        files={
            "file": (
                "sample_data.csv",
                sample_csv_bytes,
                "text/csv"
            )
        }
    )

    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
def processing_body():
    return {
        "validation": {
            "required_columns": ["student_id", "score"],
            "numeric_columns": ["score"]
        },
        "processing": {
            "remove_duplicates": True,
            "missing": {
                "enabled": True,
                "axis": "rows"
            },
            "outliers": {
                "enabled": False,
                "columns": [],
                "method": "iqr",
                "threshold": 1.5
            }
        }
    }
