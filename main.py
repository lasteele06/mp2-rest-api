import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""

    extension = Path(file.filename or "").suffix.lower()

    if extension != ".csv":
        logger.warning(f"Unsupported file format: {extension}")
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )

    # Read and parse CSV content into a DataFrame
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError
    ):
        logger.warning("Invalid CSV file")
        raise HTTPException(
            status_code=400,
            detail="Error reading CSV file"
        )

    # Save dataset to storage
    dataset_id = storage.save(df, file.filename)

    logger.info(
        f"Dataset saved with ID: {dataset_id}, "
        f"filename: {file.filename}, rows: {len(df)}"
    )

    return DatasetInfo(
        id=dataset_id,
        filename=file.filename,
        rows=len(df),
        columns=len(df.columns),
        column_names=df.columns.tolist()
    )

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""

    df = storage.get(dataset_id)

    if df is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    records = json.loads(df.head(limit).to_json(orient="records"))

    logger.info(
        f"Retrieved dataset: id={dataset_id}, "
        f"returned_rows={len(records)}"
    )

    return {
        "id": dataset_id,
        "data": records,
        "total_rows": len(df)
    }
