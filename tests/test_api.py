def test_upload_csv(client, sample_csv_bytes):
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

    data = response.json()

    assert data["rows"] == 6
    assert data["columns"] == 2
    assert isinstance(data["id"], int) and data["id"] > 0


def test_process_and_retrieve(
    client, uploaded_dataset_id, processing_body
):
    # TODO 1: Process the uploaded dataset
    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process",
        json=processing_body
    )

    assert response.status_code == 200

    data = response.json()

    # Check validation and cleaning results
    assert data["validation_rows_removed"] == 1
    assert data["cleaning_report"]["rows_before"] == 5
    assert data["cleaning_report"]["rows_after"] == 3

    # TODO 2: Retrieve the processed dataset
    response = client.get(
        f"/datasets/{uploaded_dataset_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_rows"] == 3

    records = data["data"]

    assert len(records) == 3

    actual = {
        int(record["student_id"]): int(record["score"])
        for record in records
    }

    assert actual == {
        1: 80,
        2: 90,
        5: 85
    }


def test_retrieve_missing_dataset(client):
    response = client.get("/datasets/99999")

    assert response.status_code == 404
